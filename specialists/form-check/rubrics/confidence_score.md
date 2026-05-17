---
name: confidence_score
version: 3.0.0
parent_skill: form-check
---

# Confidence-Score Rubric (v2, tiered + blast-radius + threat-model)

Every non-trivial change, plan, or review gets a score 0–100 + a tier verdict. **Threshold tiered by reversibility, not flat.**

## Why a tiered floor

A 1-line auth change ≠ a 100-line formatting change. Same rubric numbers, different stakes. Tier the threshold by the **vibe-safety axis**, same three reversibility buckets as `rubrics/vibe_safety_map.md` (vibe-safe / vibe-careful / vibe-dangerous). Vibe-impossible is handled by `rubrics/vibe_safety_map.md` as a *refusal* classification, not a score threshold.

| Tier | Threshold | Per-component minima | Trigger axis |
|---|---|---|---|
| Vibe-dangerous | ≥95 | Test ≥90, Hallucination ≥90, Adversarial ≥85, Reversibility ≥90 | auth, payments, deletes, secrets, schema-breaking, public side-effect |
| Vibe-careful | ≥90 | Test ≥80, Hallucination ≥85, Adversarial ≥70 | public API, dep add, schema-additive, prompt change |
| Vibe-safe | ≥80 | Test ≥70, Hallucination ≥70 | UI tweak, internal helper, log change |

**Pure-refactor sub-row** (rename / extract / format, no behavior change): use vibe-safe with relaxed threshold ≥70 *only if* a behavior-preservation check (golden / characterization / mutation-equivalent) passes; otherwise stay at the baseline ≥80. Pure refactor is **not a fourth tier**, it's a conditional discount on the vibe-safe threshold.

**Tier numbers tagged `[normative, operator wisdom]`.** Calibration: log every score + downstream incident outcome to `.recovery/calibration.jsonl`. After ~50 entries, retier per the empirical correlation between score-tier and incident rate.

## Components (each 0–100)

| # | Component | Weight | Full credit (100) | Half credit (50) | Zero credit |
|---|---|---|---|---|---|
| 1 | Code-read depth | 15 | every changed file end-to-end + every direct caller | skimmed touched files; trusted docstrings | did not open |
| 2 | Test verification | 20 | tests run + assertion density target met + mutation score ≥ tier-target on touched code | tests written but not run, OR run but no before/after / no mutation score | no test, no run |
| 3 | Hallucination check | 15 | every dep + API + flag + env var verified (registry, author, first-seen ≥30d, current docs) | spot-checked a few | none checked |
| 4 | Bug-class coverage | 12 | CWE Top-25 + applicable OWASP Top 10 (LLM/API/Web) + AI-PR shapes | covered the obvious 3–4 | did not consider |
| 5 | Adversarial pass | 10 | ≥3 weakest assumptions identified + falsifier per assumption + each resolved | identified weaknesses but didn't resolve | did not self-attack |
| 6 | Reversibility | 8 | irreversible ops gated; rollback documented + dry-run executed | some gates; partial rollback | free-hand destructive ops |
| 7 | Doc accuracy | 8 | CLAUDE.md / AGENTS.md / README / ADRs / fitness functions match new state | partial doc update | doc drift |
| 8 | Blast radius | 7 | scoped via `tools/blast_radius.py` (algo: `docs/blast_radius_algorithm.md`); transitive callers walked | rough estimate | not considered |
| 9 | Threat model | 5 | STRIDE applied to changed surface; LINDDUN if privacy-touching | one of the two applied | neither |

Sum = 100. **Cap headline at 99**, the remaining 1+% is unknown unknowns.

## Mutation-score targets per language

(See `multi-language/matrix.md` for the tooling matrix.)

| Language | Tool | Vibe-dangerous target | Vibe-careful target | Vibe-safe target |
|---|---|---|---|---|
| Python | `mutmut` / `cosmic-ray` | ≥75% | ≥60% | ≥40% |
| TypeScript / JS | Stryker | ≥75% | ≥60% | ≥40% |
| Java / Kotlin | pitest | ≥80% | ≥65% | ≥45% |
| Go | `go-mutesting` | ≥70% | ≥55% | ≥35% |
| Rust | `cargo-mutants` | ≥75% | ≥60% | ≥40% |

Mutation score is computed on **touched lines + their direct dependents**, not the whole codebase. If host harness can't run mutation testing, score test-verification at most 60 (component-floor) and document the gap.

## Worked example, passing (96, vibe-careful)

**Change**: add `--dry-run` flag to a CLI tool.

| # | Component | Score | Note |
|---|---|---|---|
| 1 | Code-read depth | 100 | read *cli.py*, *auditor.py* end-to-end |
| 2 | Test verification | 95 | wrote `test_dry_run_no_db_writes`; ran pytest; mutation 72% on touched lines |
| 3 | Hallucination check | 100 | no new imports |
| 4 | Bug-class coverage | 95 | dry-run is read-only; walked CWE + AI-PR shapes |
| 5 | Adversarial pass | 100 | "what if dry-run still writes via tmp DB?" → verified sqlite-utils opens lazy |
| 6 | Reversibility | 100 | no irreversible ops |
| 7 | Doc accuracy | 100 | updated CLAUDE.md + README |
| 8 | Blast radius | 95 | 2 files, internal-priv, 0 secret refs → low |
| 9 | Threat model | 90 | STRIDE walked; no surface added |

Weighted: 15(1.0)+20(0.95)+15(1.0)+12(0.95)+10(1.0)+8(1.0)+8(1.0)+7(0.95)+5(0.9) = **96.45**. Tier=vibe-careful, threshold=90, all minima met → **ship**.

## Worked example, failing (47.5, killed)

**Change**: add Redis cache to a CLI tool.

| # | Component | Score | Note |
|---|---|---|---|
| 1 | Code-read depth | 60 | read *cli.py* only |
| 2 | Test verification | 40 | integration test written, didn't run (no Redis env); no mutation |
| 3 | Hallucination check | 70 | imported `redis-py-cluster` but didn't verify `RedisCluster.from_url` exists |
| 4 | Bug-class coverage | 40 | didn't think about cache-poisoning, Redis auth, OWASP-API-08 |
| 5 | Adversarial pass | 30 | didn't ask "do we even need this?"; Newman would say no |
| 6 | Reversibility | 50 | cache writes are irreversible if poisoned |
| 7 | Doc accuracy | 0 | CLAUDE.md still says "no Redis dep" |
| 8 | Blast radius | 30 | new external dep, write-effect, lost track of secret refs |
| 9 | Threat model | 20 | STRIDE not applied to new network surface |

Weighted = **47.5**. Below every tier's floor.

**Action**: kill the change. Don't patch the score. The right move: ask "do we need a cache?" with a falsifiable success criterion ("p99 < 200ms in eval/test_baseline"). If yes, write the failing perf test first.

## Anti-gaming rules

- **Never re-weight** the rubric to make a score pass. Weights are fixed.
- **Never claim 100.** Cap at 99.
- **Verified > assumed**, when in doubt between two scores, take the lower.
- **No score-bumping without new evidence.** A re-score that uses the same inputs as the prior score is invalid.
- **Score per change**, not per project. A project has many scores.
- **Publish the score**, PR body, review report, commit trailer. Visible scores are honest scores.
- **Log every score** to `.recovery/calibration.jsonl`. Calibration data is what makes the tier numbers eventually empirical instead of normative.

## Iteration protocol

1. Score the change.
2. If headline ≥ tier threshold AND per-component minima met → ship.
3. If headline ≥ tier threshold − 5 (e.g. 85 for vibe-careful) → re-investigate the lowest-scoring component, re-score (max 30-min budget).
4. If below threshold − 5 → open a new review pass: read more code, run more tests, check more sources. Do **not** patch the score by re-weighting.
5. After 2 iterations without crossing threshold, escalate to user with a gap report (component breakdown + named blockers).

## When to spawn a verification subagent

If component scores 2 (Test) or 5 (Adversarial) sit ≤ 50, fork a verification subagent:

> Read [files]. Run [tests]. Attack the plan from the angle of [weakness]. Report back in <200 words: do you confirm or refute the proposed change is safe? Tag every claim `[verified|inferred|speculative|unknown]`.

Apply the subagent's verdict before re-scoring.

## Calibration log schema

`.recovery/calibration.jsonl`, one object per scored change:

```json
{
  "ts": "2026-05-14T19:24:00Z",
  "change_id": "PR-123",
  "tier": "vibe-careful",
  "score": 92,
  "components": {"code_read": 95, "test": 90, ...},
  "shipped": true,
  "incident": null,
  "incident_ts": null,
  "incident_severity": null
}
```

When an incident occurs, append an update row referencing the original `change_id`. Aggregation tooling (left to host) computes correlation between score-tier and incident rate. Retier when correlation is statistically meaningful (n ≥ 50 per tier).
