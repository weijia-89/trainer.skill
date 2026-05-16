---
name: skill_antipatterns
version: 2.0.0
parent_skill: form-check
---

# Skill Anti-Patterns — failure modes when applying form-check / recovery

Walk this once per engagement to ensure you're not drifting into common ways the skill gets misused or self-undermined.

## A1. Score gaming via re-weighting

**Symptom**: Score barely passes the tier floor; one component was downweighted "because it doesn't apply here."

**Failure mode**: The rubric's authority comes from fixed weights. Re-weighting hides the gap behind apparent compliance.

**Defense**: Weights are fixed by `rubrics/confidence_score.md`. If a component genuinely doesn't apply, mark `n/a-with-reason` and renormalize transparently — do not silently shift weight.

## A2. Skipping the forcing-constraint gate on scale-up

**Symptom**: Reading `scale-up/distributed_systems.md` because the feature "feels distributed."

**Failure mode**: Cargo-cult re-introduction of microservices / event bus / k8s without empirical justification. The whole point of the gate is to keep this out.

**Defense**: Run `tools/check_forcing_constraint.sh`. If exit-1, refuse and prompt the user to write the ADR. Annex chapters are read-locked behind that exit code.

## A3. Voice rules applied to API reference docstrings

**Symptom**: `tests/test_self_voice.sh` flags Sphinx-generated docstring as containing "deprecated" or other meta-language.

**Failure mode**: API reference docstrings are *required* to be uniform-shape for tooling to extract them. The deAI rules are for *prose*, not for API reference.

**Defense**: Per-archetype overlay (`templates/deai_rules.md`). API-reference overlay drops conversational hedges and allows uniform docstring shape. Skill self-test respects archetype.

## A4. Treating tier numbers as fixed truth pre-calibration

**Symptom**: User asks "why 95 for vibe-dangerous?"; reviewer cannot answer.

**Failure mode**: Tier numbers are tagged `[normative — operator wisdom]`. They're best-guess until the calibration log has ≥50 entries with incident outcomes.

**Defense**: Log every score. After 50 entries, retier per empirical correlation. State the normative tag any time you cite the threshold.

## A5. Reading scale-up content "exploratorily"

**Symptom**: User says "what would scale-up look like?" Skill quotes chapter content.

**Failure mode**: Mere knowledge of the patterns invites cargo-culting. Most enterprise patterns are right at scale and wrong out of scale.

**Defense**: Advisory mode is TOC-only. Show the chapter title and the gate criteria, not the chapter content.

## A6. Single voice across all docs

**Symptom**: README, SECURITY, CHANGELOG, ARCHITECTURE, ROADMAP all read like the same author wrote them in the same mode.

**Failure mode**: Different docs serve different consumers and conventions. Conversational SECURITY is alarming; academic README is dry.

**Defense**: Per-archetype voice (`templates/doc_voice.md`).

## A7. Walking every checklist on every change

**Symptom**: Tiny PR generates a 30-page review report citing every OWASP item.

**Failure mode**: Fatigue → noise → review skipped next time. Vibe budget is real.

**Defense**: `checklists/INDEX.md` decision tree picks applicable checklists per change shape.

## A8. Confidence rubric applied to a plan as if it were code

**Symptom**: A planning artifact gets scored 88 and "doesn't ship."

**Failure mode**: The rubric is calibrated to *code change risk*. A plan is a different artifact with different risk semantics.

**Defense**: Use the plan rubric (variant in `recovery.skill/rubrics/code_fixer_confidence.md` engagement-level scoring) for plans; the code rubric for code changes.

## A9. Mutation score reported but not run

**Symptom**: PR claims 80% mutation score; no CI evidence.

**Failure mode**: The component was designed to forbid this; vacuous self-report defeats it.

**Defense**: Mutation score must come from a runnable command in CI. If host harness can't run mutation testing, score test-verification at most 60 and document the gap.

## A10. Calibration log not maintained

**Symptom**: 6 months in; no `.recovery/calibration.jsonl` data.

**Failure mode**: The thresholds remain normative forever; the skill never empirically calibrates.

**Defense**: Per-engagement summary writes a calibration row. CI fitness function: PR cannot merge without log entry for any non-trivial change.

## A11. AGENTS.md / CLAUDE.md not updated post-change

**Symptom**: Doc accuracy component scores 100 but CLAUDE.md was last touched 3 months ago.

**Failure mode**: The component is gameable if reviewer doesn't actually diff CLAUDE.md vs current state.

**Defense**: Doc accuracy requires a verifiable diff: each change that touches surface area lists the CLAUDE.md / AGENTS.md update in the PR.

## A12. Skill drift between form-check and recovery

**Symptom**: recovery references a form-check checklist that no longer exists.

**Failure mode**: Composition without version pinning silently breaks.

**Defense**: Frontmatter `composes` declaration + `tests/test_skill_version_compat.py` verifies pinned files exist with declared version.

## How to apply

End of every engagement:
1. Walk this list (10 minutes).
2. Mark each: clean / accepted-risk-with-reason / failed.
3. If failed: fix before declaring engagement done.
