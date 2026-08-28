# Skill-tree audit, operating docs

A zero-dependency, fail-closed standing audit for the skill tree itself. Born
from a 44-finding adversarial review of the audit harness — the harness now
audits itself across five postures (SWE / AI / QA / Cyber / DevOps).

## Components

| File | Role |
|---|---|
| `tools/scan_skill_tree.py` | Structural scanner (S1–S19, C1–C9, Q1–Q6, D1–D8). Deterministic, unicode-normalized, fence-stateful, waiver-aware. |
| `tools/gate_skill_tree.sh` | Mechanical gate. Structural scan + bash/python compile + harness compile + fence balance + secret quick-scan. Exit non-zero = RED = refuse to distribute. |
| `scripts/build_manus_bundles.sh` | Atomic, lock-guarded, self-verifying Manus import-bundle builder. |
| `waivers.json` | Waiver list: `{id, path_prefix, rationale}`. |
| `tests/test_skill_tree_scan.py`, `tests/test_skill_tree_integration.sh` | Zero-dependency regression + hermetic integration tests (auto-discovered by `tests/run_all.sh`). |

## Run

```bash
# Structural scan only (writes findings JSON):
SKILL_TREE_ROOT=~/.config/opencode/skills \
SKILL_TREE_OUT=/tmp/findings.json \
python3 tools/scan_skill_tree.py

# Gate (RED => do not distribute):
bash tools/gate_skill_tree.sh

# Build Manus bundles (refuses unless gate GREEN):
bash ../../../scripts/build_manus_bundles.sh

# Full form-check suite (incl. the two tests above):
bash tests/run_all.sh
```

## Posture coverage

- **SWE (S1–S19):** frontmatter/YAML, fences, broken links, legacy refs, dead
  scripts, hardlinks, node_modules, gitignore hygiene, template drift, duplicate
  names, version-format, skill dirs without SKILL.md, nested subdirs.
- **Cyber (C1–C9):** hardcoded secrets, credential egress/beacon, look-alike
  domains, over-broad glob, secrets in context, symlink escape, world-writable,
  `.env*`/id_ files, prompt-injection (prose via `INJECT_RE` + second-opinion
  `scan_prompt_injection.sh`; code via `INJECT_RE`).
- **QA (Q1–Q6):** no tests, shell sanity, py compile, harness compile, gitignore
  drift, unpinned upstream SHAs.
- **DevOps (D1–D8):** bash `set -euo pipefail`, lock guard, atomic staging,
  count/fidelity invariant, scoped delete, rollback note, drift check,
  `bash -n`/`py_compile` gating the gate.

## Waiver schema

```json
{ "waivers": [
  { "id": "C9", "path_prefix": "specialists/x", "rationale": "..." }
] }
```

A finding is waived iff its `id` matches and `fnmatch(finding.path, path_prefix + "*")`.
Waiver-less P0–P3 => gate RED.

## Fail-closed invariants

- Missing/empty `SKILL_TREE_ROOT` => scanner exits non-zero (never a silent pass).
- Gate crashes => RED (never judges stale findings).
- `build_manus_bundles.sh` refuses to run unless `gate_skill_tree.sh` is GREEN.
- Any symlink in source => bundle build refused (zip follows symlinks).
