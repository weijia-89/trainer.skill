# Notes: ci_token_reuse

**Bug class:** over-privileged credential reuse in CI. Pull a docs-publish workflow into the prod-deploy blast radius.

**Source-of-incident pattern:** Codecov 2021 (compromised CI image used by many repos; over-privileged tokens leaked production creds); CircleCI 2023.

**Pressure axis:** velocity ("easier than provisioning"), apparent functional adequacy.

**Failure modes caught:** approval on convenience; missing the blast-radius concern.

**Cross-reference:** `SKILL.md` Section 1; `checklists/supply_chain_slsa.md` token-scoping check.
