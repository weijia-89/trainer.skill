# Skill-tree posture checklists

The 5-posture standing audit. Use these when reviewing changes to skill tooling,
or as the rubric `tools/scan_skill_tree.py` enforces. Severity bands: P0 (blocker) →
P3 (watch). Green == 0 open P0–P3 after waivers.

## SWE posture (S)
- [ ] S1 frontmatter valid YAML; `name`+`description` present
- [ ] S2 code fences balanced (stateful, fixture-validated)
- [ ] S4 no broken relative links in prose (fences masked)
- [ ] S5 no legacy `skill-creator`/hardcoded adapter refs
- [ ] S6 no dead/broken scripts referenced
- [ ] S7 no hardlinks
- [ ] S8 `node_modules` absent from tree
- [ ] S9 `.gitignore` covers artifacts
- [ ] S10 template drift (old versions referenced)
- [ ] S11 duplicate skill names
- [ ] S12 world-writable / escape symlinks
- [ ] S13 `.env*` / `id_*` / `*secret*` not bundled
- [ ] S14 skill dir without `SKILL.md`
- [ ] S15 unexpected nested subdirs

## Cyber posture (C)
- [ ] C1 no hardcoded secrets (key, token, private key)
- [ ] C2 no unpinned/look-alike egress or beacon URLs
- [ ] C3 no over-broad glob delete (`rm -rf $VAR/*`)
- [ ] C4 secrets not pasted into context/logs
- [ ] C5 no credential written to world-readable path
- [ ] C6 symlink escape refused
- [ ] C7 no unauthenticated credential access path
- [ ] C8 no supply-chain (unpinned upstream SHA where policy requires pin)
- [ ] C9 prompt-injection (prose + code) caught

## QA posture (Q)
- [ ] Q1 every skill with code has tests
- [ ] Q2 `bash -n` clean on all `.sh`
- [ ] Q3 `py_compile` clean on all `.py`
- [ ] Q4 harness (audit tooling) itself compiles
- [ ] Q5 no gitignore drift for generated artifacts
- [ ] Q6 upstream SHAs pinned (where policy requires)

## DevOps posture (D)
- [ ] D1 `set -euo pipefail` on publish scripts
- [ ] D2 lock guard (single concurrent build)
- [ ] D3 atomic staging (move-in-first swap)
- [ ] D4 count invariant (src dirs == published bundles)
- [ ] D5 scoped delete (operator zips preserved)
- [ ] D6 rollback = re-run from source (idempotent)
- [ ] D7 content-drift check before declare GREEN
- [ ] D8 gate gates the gate (gate GREEN before build)

## Loop rule
Re-run after every change. Any new >P3 => fix, then re-run until clean. This is
the same discipline the audit harness applies to itself.
