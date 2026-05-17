---
name: forcing_constraint_check_algorithm
version: 2.0.0
parent_skill: form-check
status: algorithm spec
---

# Forcing-constraint check algorithm (manual)

For hosts that can't run `tools/check_forcing_constraint.sh`. Used by `scale-up/*` chapters.

## Inputs

A repository path. The check verifies whether `<repo>/docs/adr/` contains an ADR satisfying all three:

1. `Type: forcing-constraint` (or `type: forcing-constraint`)
2. `Status: accepted` (case-insensitive)
3. `constraint_class:` is set (any of: `regulatory`, `scale-measured`, `org-mandate`)

## Procedure (manual)

1. List `<repo>/docs/adr/*.md`.
2. For each file, check the front-matter or header section for the three keys.
3. If at least one file satisfies all three: pass (exit 0 in the script).
4. If at least one file has type=forcing-constraint and status=accepted but is missing `constraint_class`: malformed (exit 2 in the script). This is a fixable state, the ADR exists but doesn't carry the required metadata.
5. Otherwise: no forcing constraint (exit 1 in the script). Default-mode applies.

## Outputs

- **Pass**: scale-up chapters may be consulted.
- **Malformed**: prompt user to fix the ADR (likely missing `constraint_class:` field). Do not consult scale-up chapters.
- **None**: refuse scale-up content. Operate in advisory mode (TOC only).

## Anti-patterns

- Treating the *existence* of an ADR as the gate, regardless of `Status`, proposed/draft is not accepted.
- Treating the gate as advisory ("I'll just read the chapter"), defeats the purpose.
- Checking only one file location and missing ADRs in nested directories, the script and this algorithm walk all `*.md` under `docs/adr/`.

## Forcing-constraint ADR template

`templates/forcing_constraint_adr.md`, required structure that this check validates.
