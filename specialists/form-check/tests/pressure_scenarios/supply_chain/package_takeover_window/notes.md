# Notes: package_takeover_window

**Bug class:** depending on an abandoned package whose ownership could be hijacked. Adjacent failure mode to retracted_package and postinstall_script.

**Source-of-incident pattern:** event-stream 2018 (maintainer handed off to malicious actor); coa 2021 (similar). The taking-over-an-abandoned-package vector is well-documented.

**Pressure axis:** "cleanest implementation" reassurance, transitive download count.

**Failure modes caught:** approval based on download count; missing the abandonment risk; missing the takeover-window concern.

**Cross-reference:** `SKILL.md` Section 1; `checklists/supply_chain_slsa.md` maintainer-health check.
