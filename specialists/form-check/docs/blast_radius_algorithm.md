---
name: blast_radius_algorithm
version: 2.0.0
parent_skill: form-check
status: algorithm spec
---

# Blast-radius algorithm (manual / language-portable spec)

For hosts that can't run `tools/blast_radius.py`, apply this algorithm by hand. Reference for component 8 of `rubrics/confidence_score.md`.

## Inputs

- `n_files`: number of files in the change diff
- `privilege_label`: highest-privilege axis touched
- `call_paths`: distinct call sites referencing changed symbols
- `secret_handling_bonus`: did the change touch env-var or secret patterns?

## Privilege weights

| Pattern in changed path | Label | Weight |
|---|---|---|
| `api/` or `public/` | public-api | 30 |
| `db/` or `migrations/` or `schema/` | write-effect | 30 |
| references `auth`, `password`, `secret`, `token`, `crypto` | secret-handling | 30 |
| `admin/` | write-effect | 25 |
| styles, docs | internal | 5 |
| (anything else) | internal | 5 |

Take the **max** weight across all changed files.

## Call-paths estimate

Cheap heuristic: for each changed source file, count grep hits across the repo for the file's basename (excluding the file itself). Bound at the language level (`.py`, `.ts`, `.js`, `.java`, `.kt`, `.go`, `.rs`).

For deeper accuracy, use a language-aware tool (LSP-based "find references"). The skill ships the heuristic; deeper tooling is a host concern.

## Secret-handling bonus

If any changed file's source matches `env\[`, `getenv`, `os.environ`, `process.env`, or `System.getenv`: +20.

## Score formula

```
files_term     = log10(n_files + 1) * 20
paths_term     = log10(call_paths + 1) * 15
score          = min(100, round(files_term + privilege_weight + paths_term + secret_handling_bonus))
```

Cap at 100. Below 30 = low blast radius. 30–60 = medium. 60+ = high.

## Examples

| Diff | n_files | privilege | paths | secret | Computed |
|---|---|---|---|---|---|
| 1 file, internal helper, 0 callers | 1 | internal (5) | 0 | 0 | 6.0 + 5 + 0 + 0 = ~11 (low) |
| 5 files in `api/`, 12 callers | 5 | public-api (30) | 12 | 0 | 15.6 + 30 + 16.2 + 0 = ~62 (high) |
| 1 file in `auth/`, 3 callers, references env | 1 | secret-handling (30) | 3 | 20 | 6.0 + 30 + 9.0 + 20 = ~65 (high) |
| 20 files in `db/migrations/`, transitive 50 | 20 | write-effect (30) | 50 | 0 | 26.4 + 30 + 25.5 + 0 = ~82 (very high) |

## Tags

This is a *heuristic*, not a precise measurement. Tag scoring outputs as `[approximate]` per `epistemic-planning` discipline.
