# superset.skill ROADMAP

**Current version:** v0.3.0 (bundled as 9th specialist in trainer.skill v0.7.1; renamed from `ancillary` in this version)
**Status:** working draft. The five-pillar template and falsifier checklist are stable and have caught real failures in v0.1.x production sessions under the previous name. The 0.2.0 additions (role archetypes, batch-aggregation, runtime portability) are documented but have not yet been pressure-tested across a multi-batch run. v0.3.0 is a pure rename for trainer-family coherence; no behavioral changes.

## Near-term

- **Pressure-test the v0.2.0 additions.** Run at least one parallel batch using each role archetype (`sweep`, `prose-audit`) and capture the session logs against the falsifier checklist. Targets: the lodestar em-dash sweep pattern as the `sweep` test bed, a career-help cover-letter audit as the `prose-audit` test bed.
- **Validate the batch-aggregation template** on a real 3-agent batch with at least one partial-failure agent, so the failure decision matrix gets exercised in practice rather than only on paper.
- **Worked example writeup** for the most-instructive past dispatch (TC-9030 oracle-pilot move, which fired H5 in production), so the skill has a concrete reference instead of only abstract rubrics.

## Mid-term

- **Test-fix and integration role overlays.** Two additional archetypes that overlap with `code` but have distinct verification shapes. Add when triggered by real recurring use cases, not before; YAGNI applies.
- **Cross-runner validation.** The runtime-portability reference covers Cascade-on-Windsurf and Claude Code from direct experience; Cursor, Codex, and Gemini CLI entries are best-effort drafts. Validate each by running one parallel batch on each runner.
- **Failure-mode log.** A running list of "superset did not catch this" cases so the skill's blind spots are visible to future iterations. Pattern borrowed from `diet.skill/ROADMAP.md`.

## Out of scope

- A live message bus or DAG executor. The fresh-chat dispatch model treats agents as one-shot and assumes the operator is the only coordination channel between them. Adding a runtime bus would reinvent `orchestrator-supaconductor`; users who want that should use that project instead.
- A desktop UI. `usemozzie/mozzie` exists for that use case.
- An auto-retry policy for failed agents. The trainer's coached-override pattern caps retries at two manual rounds; the operator owns the decision, and the orchestrator stays out of the loop.
- A formal DAG specification language. The `Phase:` header field captures the only sequencing constraint that has come up in practice (scaffold-then-features). More elaborate dependencies belong in separate batches and stay out of the prompt itself.

## Open questions

- Whether the `sweep` overlay should ship a sample regex-validation harness or stay prose-only. Risk of the harness: it creates a false floor where agents trust the harness output without sanity-checking individual matches.
- Whether the orchestrator-handoff template should embed a state-verification command set per project type, or stay generic. The generic version transfers cleanly; the per-project version is more useful but bloats the template.
- Whether to add a `Risk-tier:` header field (vibe-safe / vibe-careful / vibe-dangerous) that gates which verification commands run. Currently the agent declares the tier in First Steps; making it a header field is more explicit but adds a field every prompt has to fill.
- Whether to bundle a `verify_superset_sync.sh` script (matching the trainer.skill pattern) when the canonical and `.claude/skills/` mirror diverge.

## Validation status

Each major pattern in this skill has a validation status. The skill ships claims at the level of evidence behind them.

| Pattern | Status | Evidence |
|---|---|---|
| Five-pillar prompt template | Validated | v0.1.x sessions on `lodestar`, `mailchimp-r-and-a-qa-suite`. |
| H1-H8 falsifiers | Validated | Each fired at least once in v0.1.x sessions. |
| H9 (gitignore pre-flight) | Pattern-validated, project-validated | Documented in `obra/superpowers-skills`. Not yet fired in a superset session because all v0.1.x projects already had `.worktrees/` gitignored. |
| H10 (project-setup auto-detect) | Pattern-validated | Documented in `obra/superpowers-skills`. Not yet validated in a superset multi-language batch. |
| M11 (Owned-paths table) | Pattern-validated | Borrowed from `usemozzie/mozzie`. Not yet validated in a superset batch with >3-file scope per agent. |
| M12 (Phase field) | Mozzie-validated | Mozzie's CLAUDE.md uses this. Not yet validated in a superset scaffold-then-features batch. |
| Role archetypes | Drafted | Documented in `references/role-overlays.md`. Pressure tests pending (see near-term). |
| Batch-aggregation template | Drafted | Synthesized from `subagent-driven-development` (obra) + `parallel-dispatch` (supaconductor) + operator-review-bandwidth concern. Not yet pressure-tested end-to-end. |
| Runtime portability | Partial | Cascade-on-Windsurf direct experience. Claude Code from `Task`-tool documentation. Cursor, Codex, Gemini CLI from secondary sources; validation pending. |
