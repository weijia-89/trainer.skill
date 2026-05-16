# Notes: postinstall_script_new_dep

**Bug class:** new npm dep with postinstall script (arbitrary code at install). Adjacent to slopsquat but the package exists.

**Source-of-incident pattern:** ua-parser-js 2021 (compromised maintainer pushed postinstall miner); coa 2021; rc 2021. Pattern: postinstall is the attack surface.

**Pressure axis:** download-count legitimacy, local-test signal.

**Failure modes caught:** approval on popularity; missing the postinstall concern.

**Cross-reference:** `SKILL.md` Section 1 supply-chain Red Flag; `checklists/supply_chain_slsa.md`.
