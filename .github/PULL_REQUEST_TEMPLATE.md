## Summary
<!-- One paragraph. What this PR does and why. No jargon. A non‑engineer should understand the intent. -->

## Changes
<!-- One bullet per logical change. -->
- `path/to/file`: what changed and why.

## Test plan
### Automated (required)
- [ ] `GITHUB_ACTIONS=true GITHUB_WORKSPACE=$PWD bash scripts/verify_trainer_sync.sh` – all invariants PASS
- [ ] `shellcheck scripts/check_pr_merged.sh` – clean, no warnings (if the file exists)
- [ ] `shellcheck scripts/install_hooks.sh` – clean, no warnings (if the file exists)
- [ ] Generation gate (`generation_gate.sh --strict`) – warnings pre‑existing, no functional impact
- [ ] `python3 scripts/verify_autonomous_code_review.py --repo-root .` – PASS

**Coverage notes:** <short sentence what the tests cover and what they do not; why the gaps are acceptable.>

## Notes
<!-- Required even if "None". Deviations, risks, follow‑ups. -->

---
### R‑6 user‑facing docs
If this PR changes any of `scripts/`, `references/`, `prompts/`, `.github/`, `specialists/`, `mirrors/`, either
* update the listed docs (CHANGELOG.md, README.md, ROADMAP.md, SECURITY.md) **or**
* add the line `R-6 waived` in the reviewer comment (see `.github/REVIEW_COMMENT_TEMPLATE.md`).