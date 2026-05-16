---
name: code_fixer_confidence
version: 2.0.0
parent_skill: recovery
composes: form-check.rubrics.confidence_score@2.0.0
---

# Codeit Confidence Rubric (v2 — composes form-check, no duplication)

The recovery engagement uses **all 9 components from `form-check.skill/rubrics/confidence_score.md`** plus 2 engagement-specific. Total weight rebalanced to sum to 100.

## Inherited components (rebalanced 0.9× from form-check)

| # | Component | form-check weight | recovery weight |
|---|---|---|---|
| 1 | Code-read depth | 15 | 13.5 |
| 2 | Test verification | 20 | 18 |
| 3 | Hallucination check | 15 | 13.5 |
| 4 | Bug-class coverage | 12 | 10.8 |
| 5 | Adversarial pass | 10 | 9 |
| 6 | Reversibility | 8 | 7.2 |
| 7 | Doc accuracy | 8 | 7.2 |
| 8 | Blast radius | 7 | 6.3 |
| 9 | Threat model | 5 | 4.5 |

Subtotal: 90.

## Codeit-added components

| # | Component | Weight | Full credit |
|---|---|---|---|
| 10 | Workflow completeness | 7 | every required phase ran; verdicts logged to `.recovery/state.jsonl`; abort protocol available |
| 11 | Voice integrity | 3 | deAI sweep clean across docs (no banned vocab outside `references/`/`examples/`); per-archetype overlay applied |

Subtotal: 10. **Total: 100.**

## Tier thresholds (inherited from form-check)

| Tier | Threshold | Per-component minima (delta vs form-check) |
|---|---|---|
| Vibe-dangerous | ≥95 | + Workflow completeness ≥85, Voice integrity ≥80 |
| Vibe-careful | ≥90 | + Workflow completeness ≥80, Voice integrity ≥70 |
| Vibe-safe | ≥80 | + Workflow completeness ≥70 |
| Pure refactor | ≥70 | (no recovery add-ons; pure refactor unlikely to invoke recovery) |

Same calibration log used (`.recovery/calibration.jsonl`). Codeit appends a row per engagement-level score AND per per-change score; the log tags `engagement_level: true|false`.

## Anti-duplication rule

This rubric **must not** restate form-check component definitions. If component definitions diverge between skills, recovery's self-test (`tests/test_skill_version_compat.py`) fails. To change a component definition, edit `form-check.skill/rubrics/confidence_score.md`, bump its version, and update the `composes` pin in `recovery.skill/SKILL.md`.

## Worked engagement-level example (94, vibe-careful)

Engagement: harden a small TypeScript service (1k LOC, 4 endpoints, no AI).

| # | Component | Score |
|---|---|---|
| 1–9 | inherited from per-change rollups (mean) | 94.2 |
| 10 | Workflow completeness | 95 (all phases ran; one phase escalated to user with gap report; clean state.jsonl) |
| 11 | Voice integrity | 90 (1 banned-vocab miss in CHANGELOG flagged; fixed) |

Weighted = 13.5(0.94)+18(0.94)+13.5(0.94)+10.8(0.94)+9(0.94)+7.2(0.94)+7.2(0.94)+6.3(0.94)+4.5(0.94)+7(0.95)+3(0.90) = **94.13**.

Tier=vibe-careful (engagement default for harden), threshold=90 ✓, minima met ✓ → **engagement passes**. Per-change scores still apply to individual rewrites within the engagement.

## Phase-level mini-scores

Each phase emits a partial score reflecting only the components it can compute:

| Phase | Components scored |
|---|---|
| discovery | (none — meta phase) |
| review | 1, 4, 5, 9 |
| scoring | aggregates per-change scores |
| doc-pass | 7, 11 |
| deAI-sweep | 11 |
| adversarial | 5 |
| launch-ready | aggregates everything |
| summary | reports headline + per-tier breakdown |

Per-change scores (within an engagement) use the full 11-component rubric. Engagement-level score is the weighted aggregate plus components 10–11.
