---
name: smell_catalog
version: 2.0.0
parent_skill: form-check
---

# Month-3 Smell Catalog

Failure modes that surface ~3 months after launch. Watch for these by archetype. The original v1 named specific projects (`wcag-auditor`, `network-scanner`, `no-log-rsvp`, `android-hardener`); examples now in `examples/per_archetype_smells.md`.

## Generic (any project)

1. **Tests pass but feature is broken** — coverage was path-exercising, not behavior-asserting. Fix: write a few property-based tests; add eval gates; mutation-test on touched code.
2. **Doc drift** — CLAUDE.md / AGENTS.md says X, code does Y. Fix: doc-as-code lint; pre-commit grep; fitness function.
3. **Eval baseline ratchets up but real users complain** — golden dataset overfit to early bugs. Fix: rotate dataset; add prod-shadow inputs.
4. **One module ate the codebase** — every change touches it. Fix: Parnas re-decompose; the module hides multiple decisions, not one.
5. **No one reads the diffs** — vibe budget exceeded; PRs land with surface-level review. Fix: enforce review-gate test for vibe-dangerous list; per-tier per-component minima.
6. **Calibration log abandoned** — score-vs-incident correlation never computed; thresholds remain normative forever. Fix: quarterly calibration review.
7. **Fitness functions wired but not maintained** — green CI but ADRs evolved past the function. Fix: quarterly architecture review; functions are first-class artifacts.
8. **Slopsquatted dep snuck in** — junior dev / agent added `easy-yaml` (real: `pyyaml`). Fix: dependency review template requires slopsquatting trail; CI dep audit.

## CLI tools

9. **Subprocess leak** — child processes accumulating. Fix: language-native subprocess context manager + timeout.
10. **Cache poisoning** — local cache holds stale or attacker-influenced data. Fix: TTL + content-hash verification.
11. **`--apply` mode shipped because someone wanted it** — review-gate rule violated. Fix: revert; require ADR with "won't auto-apply" rule preserved.
12. **Embedded reference data drift** — OUI vendors, CIS benchmarks, geoIP DB age out. Fix: scheduled job to refresh + lint test.
13. **Stable JSON schema for `--format json` quietly broke** — downstream pipeline broke. Fix: schema versioning; SemVer of CLI output.

## Web / API services

14. **PII logging snuck back in** — debug log from a hotfix forgot redaction. Fix: lint rule + pre-commit grep.
15. **TTL deletion job silently failed** — cron didn't run; DB filled up. Fix: alert on "0 rows deleted by GDPR job in last 24h"; idempotent retries.
16. **Token reuse / replay** — RSVP / one-time token verified but not single-use. Fix: idempotency table; OWASP-API-2023 walk on the surface.
17. **EXIF / metadata scrubbing missed XMP / IPTC** — only EXIF tags removed. Fix: property test against the canonical metadata library.
18. **Rate-limit bypass via auth-state** — anonymous limit lower than authenticated; attacker keeps a stale-but-valid token to enjoy higher quota. Fix: tier-aware rate limits; behavioral signals.
19. **OpenAPI schema diverged from runtime** — consumers broke silently. Fix: contract test in CI; fitness function.

## LLM-bearing modules

20. **Prompt rev drifted; eval gate didn't catch** — prompts changed in PR but baseline was stale. Fix: prompt versioning + auto-eval on PROMPT-MAJOR / MINOR.
21. **Model upgrade broke parsing** — provider rolled out a new model; output JSON shape shifted. Fix: pin model; run shadow-eval for 1 week before upgrade.
22. **RAG poisoning** — adversarial content in indexed corpus changes retrieval results. Fix: source-trust scoring; provenance tracking; quarantine on prompt-injection signature.
23. **Token-budget runaway** — single user can drive arbitrary cost. Fix: per-tenant rate + token + cost quotas; alerts on outlier traffic.
24. **System-prompt leakage exposed business rules** — model can be coaxed to reveal system prompt; rules were in prompt, also enforce server-side. Fix: defense in depth — never rely on prompt as only gate.

## Library / package archetype

25. **Public API drift** — minor version changed signature, broke consumers; SemVer violation. Fix: API surface tests in CI; deprecation policy with Sunset header equivalent for libraries.
26. **Docs-gen broke on docstring inconsistency** — Sphinx fails on mixed format; deploy red. Fix: per-archetype voice rules (`recovery.skill/templates/doc_voice.md`); uniform docstring shape required.
27. **Dependency confusion** — private package name registered on public registry; CI consumed the public one. Fix: scope packages (`@org/name`); publish-on-private-only flag.

## Monorepo archetype

28. **Cross-app dep change broke another app silently** — change reviewed in app A, broke app B's CI. Fix: monorepo affected-graph (Nx / Turborepo / Bazel) running both apps' tests on package changes.
29. **Versioning model drifted** — declared "fixed across monorepo" but apps started releasing independently. Fix: ADR re-decision; tooling enforces.
30. **Cross-language type schemas diverged** — Python service and TS web app consumed the same logical entity but with different shapes. Fix: shared-schemas package as single source; codegen per language; CI verifies consistency.

## Per-archetype examples

Worked examples (specific failure scenarios, fix patterns) in `examples/per_archetype_smells.md`.

## Output during review

For each project archetype:
- Walk the relevant generic + archetype-specific smells.
- Mark each: not-yet-applicable / latent-risk / observed-already-fix-pending / fixed.
- For "latent-risk": file in ROADMAP "Next" with detection signal.
- For "observed": create P0/P1/P2 finding with reproduction.
