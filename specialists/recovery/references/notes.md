---
name: references
version: 2.0.0
parent_skill: recovery
inherits: form-check/references/notes.md
---

# References — recovery

Codeit composes `form-check`. All citation tags resolve via `form-check/references/notes.md`. This file lists tags recovery *adds* beyond form-check's set.

## Codeit-specific tags

(None at v2.0.0 — recovery is a workflow / composition skill; substantive citations live in form-check.)

When recovery adds a citation in future versions, append a row here mirroring the schema in form-check's `notes.md`.

## Cross-reference

For any tag used in recovery content, the resolution order is:
1. This file (recovery-specific tags)
2. `form-check/references/notes.md`
3. Upstream archive `localonly/code-skills-overhaul-archive/REFERENCES.md` (no longer actively maintained; for historical reference only)

`tests/test_citations.py` verifies orphan-free across both skills.
