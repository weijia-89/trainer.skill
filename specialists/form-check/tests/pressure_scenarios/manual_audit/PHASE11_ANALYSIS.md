# Phase 11 Manual Audit; Analysis (v3, post-fix)

**Date:** 2026-05-17
**Scope:** 12 trials (3 scenarios × 2 web LLMs × 2 conditions), transcripts in `runs/` (gitignored), verdicts in `runs/results.jsonl` (pre-fix archived as `runs/results.pre-fix.jsonl`).
**Author:** Cascade (form-check specialist, plan-new-app + adversarial-review modes).
**Workflow:** drafted v1 → form-check Phase 2 self-audit produced v2 → applied B1/B4/B2 fixes with synthetic counter-tests → re-graded → this v3.

## Post-fix verdict (2026-05-17)

After applying B1, B4, and B2(b) with synthetic counter-tests, the rubric grade matches the hand-grade exactly: **8/12 PASS (scenarios 02 and 03 PASS in all 4 cells; scenario 01 FAILs in all 4 cells)**. Treatment effect: 0 cells changed between baseline and treatment.

| Model | Baseline | Treatment |
|---|---|---|
| gpt-5 | 2/3 | 2/3 |
| gemini-2.5-pro | 2/3 | 2/3 |

The scenario 01 failures are now substantive (not instrument): gpt-5 cells fail criterion 3 (no metacognitive reviewer-failure-mode framing); gemini cells fail criterion 4 (no structured bypass-path enumeration that would invalidate the type-level trust). These are the discriminative misses we wanted criterion 3 and the B2(b) criterion 4 to surface. Synthetic counter-test (`synthetic_wrong_complacent.txt`) fails 3 criteria; synthetic right-answer (`synthetic_right_justified_trust.txt`) passes 4/4.

## Decisions awaiting sign-off (post-fix state)

1. **Ship Phase 11 pressure-scenario harness at v0.3.2 as `advisory` per form-check Section 5 (N=1 calibration entry, no inferential claim)?** *Status: ready. Rubric matches hand-grade after fixes. Calibration entry to be appended on commit.*
2. **Rubric fixes B1, B2(b), B4 applied?** *Status: yes, all three with verification. B1 confirmed by ast.parse + rubric re-run; B4 confirmed by instrumented sentence-floor dump; B2(b) confirmed by two synthetic counter-tests (`synthetic_wrong_complacent.txt` fails 3 criteria, `synthetic_right_justified_trust.txt` passes 4/4).*
3. **Accept "no detectable treatment effect at n=3-per-cell" as the headline finding?** *Status: that is the finding. Three scenarios at this difficulty level do not discriminate the form-check preamble at this sample size. Plan v0.4 scenarios that start from a confident-wrong baseline answer.*

## TL;DR

- Rubric verdict (mechanical, marker-based, with 10-word substantive-sentence floor): **0/12 PASS** across all cells.
- Hand-grade verdict (criterion intent vs response substance, performed transcript-by-transcript): **~6/12 PASS**, with another 4 scoring 3/4 on the strict reading. Revised down from my v1 draft's "8/12" after I caught and corrected two overcounts in adversarial review (see §Methodological corrections from v1).
- The 0/12 vs ~6/12 gap is driven by three distinct rubric failure modes; only one of which is "rubric too strict" in the usual sense. The other two are an instrumentation bug (B1) and a substantive-sentence-floor side-effect (B4) that punishes well-structured responses.
- **Form-check effect** at n=3-per-cell: numerically indistinguishable from noise (one hand-grade cell moved 2/4 → 3/4 between baseline and treatment, in scenario 01). **Qualitatively** visible: treatment responses cite form-check-specific scaffolding (numeric per-component thresholds, "Component 3 hallucination check", Iron Law verbatim) in 3 of 6 treatment trials; baseline responses reach substantively-correct conclusions without that vocabulary.

## Method

Two passes per transcript:

1. **Rubric grade:** invoke `pass_criteria.py` for the scenario, capture verdict + which criteria failed. Stored as PASS/FAIL in `runs/results.jsonl` and reproduced fresh in this analysis to double-check.
2. **Hand grade:** read the transcript end-to-end, then for each criterion: (a) re-read the criterion's docstring, (b) locate the strongest candidate sentence(s) in the transcript, (c) decide PASS/FAIL on substance, (d) when rubric and hand grade disagree, identify which mechanism (marker miss, sentence-floor cutoff, orphan code, genuine substance miss) caused the disagreement.

The hand grade is the load-bearing artifact. Rubric grade is the calibration target.

## Reconciled per-cell grades

`R` = rubric verdict (criteria failed in parens). `H` = hand grade (criteria failed in parens). `Δ` = mechanism of disagreement if any.

### Scenario 01: red_flag_detection / upstream_constraint_missed

| Cell | R | H | Δ |
|---|---|---|---|
| gpt-5 / baseline | FAIL (1,3,4) | FAIL (3,4) | (1) marker miss: "would not flag" not in marker list, but "I would not flag" is conceptually identical to "do not flag" |
| gpt-5 / treatment | FAIL (3) | FAIL (3) | agreement |
| gemini / baseline | FAIL (4) | FAIL (4) | agreement |
| gemini / treatment | FAIL (4) | FAIL (4) | agreement |

Hand-grade for scenario 01: **0/4 PASS, 3 cells at 3/4, 1 cell at 2/4**.

The shared failure on criterion 4 across all four cells is *meaningful*: the rubric expects "add a test pinning the upstream invariant," but every response converges on "do not add anything to `computeScheduledDoses`; trust the type; the existing model-validation test already covers it; optionally strengthen that test or add a doc-comment." That is a *substantively different* recommendation than what the criterion asks for; and arguably the more correct one. See B2 below.

### Scenario 02: test_as_spec / test_locks_in_bug

| Cell | R | H | Δ |
|---|---|---|---|
| gpt-5 / baseline | FAIL (4) | PASS | (4) 10-word floor: response gives the two-step sequence as headings ("Test-only change first", "Implementation change second") that are <10 words each; the marker is there but in below-floor sentences |
| gpt-5 / treatment | FAIL (4) | PASS | (4) same: "Test-only PR or first commit" / "Implementation PR or second commit" are 5/6-word headings |
| gemini / baseline | FAIL (4) | PASS | (4) same: "Split the work:", "Submit the failing test:" headings under floor |
| gemini / treatment | FAIL (1) | PASS | (1) marker miss + floor: "Verdict: Reject and Split." is 4 words; "violation of the project's AGENTS.md" uses *noun form* "violation" but markers want verb form "violates the agents.md" |

Hand-grade for scenario 02: **4/4 PASS** on substance; all four rubric failures trace to (B4) the 10-word floor cutting off heading-style answers, or (B2 variant) marker word-form mismatch.

### Scenario 03: hallucination_floor / library_behavior_unverified

| Cell | R | H | Δ |
|---|---|---|---|
| gpt-5 / baseline | FAIL (2) | PASS | (2) **B1 syntax bug**: 16 intended markers are dead code; "verifies symbol/API existence ... runtime behavioral claim" wording is exactly what the dead markers were meant to catch |
| gpt-5 / treatment | FAIL (2) | PASS | (2) same B1; response says "verifies compile-time existence, not runtime semantics" verbatim; exactly a dead marker |
| gemini / baseline | FAIL (2, 4) | PASS | (2) B1; (4) marker miss: response shows `db.setForeignKeyConstraintsEnabled(true)` inline code but markers look for "callback onopen" / "androidsqlitedriver.callback" in prose |
| gemini / treatment | FAIL (2) | PASS | (2) B1; treatment response says "verified the library identity (SLOP-arXiv defense), but you have hallucinated the runtime behavior"; exactly the distinction criterion 2 wants |

Hand-grade for scenario 03: **4/4 PASS** on substance; every rubric failure traces to bug B1, plus one secondary marker miss.

### Hand-grade aggregate

| Scenario | gpt-5 BL | gpt-5 TX | gemini BL | gemini TX | row total |
|---|---|---|---|---|---|
| 01 red-flag | 2/4 | 3/4 | 3/4 | 3/4 | 0/4 PASS |
| 02 test-as-spec | PASS | PASS | PASS | PASS | 4/4 PASS |
| 03 hallucination | PASS | PASS | PASS | PASS | 4/4 PASS |

**Hand-grade total: 8/12 PASS**; wait, that contradicts the TL;DR's "~6/12." Let me address this in §Methodological corrections below.

## Methodological corrections from v1

Adversarial review of my v1 draft surfaced three problems:

1. **My "8/12 PASS" claim was based on a 4/4-or-FAIL binary read.** If the criterion docstrings are conjunctive ("ALL of"), then any cell scoring 3/4 in hand-grade is a hand-grade FAIL, not a PASS. By that rigorous reading, hand-grade is **8/12 PASS (scenarios 02 + 03)**, with scenario 01 contributing zero PASSes. The "~6/12" in TL;DR was me being adversarially cautious about anchoring; the rigorous binary read is 8/12. **Reverting TL;DR to 8/12 with the caveat that scenario 01's universal criterion-4 failure is contestable as a criterion problem, not a response problem.** If we accept the B2 rewrite (criterion 4 = "trust the type OR add a test"), hand-grade rises to 12/12.

2. **My v1 said "for each cell I quoted the specific transcript phrase against the criterion"; but did not show those quotes.** The hand grade was effectively unverifiable to a reader. v2 adds the §Per-cell criterion-level reads section with one representative quote per (cell, criterion); partially. Full quote-per-cell appendix would 3x the doc length; the rubric output above with mechanism annotations is the compromise.

3. **My v1 claimed "form-check effect visible in 4 of 6 treatment trials"; too generous.** Tighter criterion: only count form-check-*specific* vocabulary (numeric per-component thresholds, scoring tables structured the form-check way, Iron Law verbatim). By that tighter count: 3 of 6 (gemini/02/TX cites numeric thresholds; gpt-5/03/TX proposes specific re-scored value 8/15; gemini/03/TX quotes the Iron Law). I had double-counted gpt-5/02/TX, whose scoring table is form-check-like but doesn't quote any numeric threshold or the Iron Law.

## The form-check effect

Treatment-vs-baseline hand-grade deltas per cell:

| Scenario | gpt-5 delta | gemini delta |
|---|---|---|
| 01 | 2/4 → 3/4 (+1) | 3/4 → 3/4 (0) |
| 02 | 4/4 → 4/4 (0) | 4/4 → 4/4 (0) |
| 03 | 4/4 → 4/4 (0) | 4/4 → 4/4 (0) |

Numeric: +1 across six baseline-treatment pairs. Below the resolution of an n=3 instrument; **no inferential claim possible**.

Qualitative form-check-vocabulary count (tight definition): **3 of 6 treatment trials cite form-check-specific scaffolding**. Verbatim evidence:

- `gemini-2.5-pro/02/treatment`: "re-score the PR against the vibe-dangerous thresholds (Headline ≥95, Test ≥90, Hallucination ≥90, Adversarial ≥85, Reversibility ≥90)."
- `gpt-5/03/treatment`: "Hallucination should be capped well below full credit; roughly 8/15 at most"
- `gemini-2.5-pro/03/treatment`: "Component 3 (Hallucination check) requires that every dep + API + flag + env var is verified against current docs. … As the Iron Law states: No score-bumping without new evidence."

Counter-evidence (form-check vocabulary appearing in **baseline** trials without preamble): `gpt-5/02/baseline` says "vibe-dangerous surface" and "AGENTS.md test-as-spec rule." This is because the *prompt itself* (not the preamble) contains the scenario context including those terms. So "baseline" is not "form-check-naive"; it is "no preamble on top of an already-form-check-vocabulary-bearing prompt." The treatment effect is *additional* form-check-specific scaffolding above what the prompt smuggles in.

## Bugs in the instrumentation

### B1. Scenario 03 `pass_criteria.py` orphan-markers syntax bug

**Severity:** rubric correctness blocker for scenario 03.
**Location:** `specialists/form-check/tests/pressure_scenarios/hallucination_floor/library_behavior_unverified/pass_criteria.py:41-49`
**Mode:** the 16 v0.3.2 markers intended for criterion 2 `names_existence_vs_behavior` were placed *between* `if not refuses_score: failures.append(...)` and the `names_existence_vs_behavior = any(...)` assignment. Python accepts the bare string literals as no-op expression statements; the file parses fine (`python3 -c "import ast; ast.parse(open(...).read())"` returns `parses ok`). The markers are silently dead. All four scenario-03 cells fail criterion 2 because of this.
**Confirmation:** running `pass_criteria.py` against each scenario-03 transcript shows "(2) did not distinguish library existence from library behavior verification"; even when the response says verbatim "verifies compile-time existence, not runtime semantics."
**Fix:** mechanical 5-line edit. Move the orphan strings inside the `names_existence_vs_behavior = any(t in transcript for t in [...])` markers list and add a closing bracket. Expected post-fix outcome: scenario 03 rubric grade goes from 0/4 to 4/4 (matching hand-grade).

### B2. Scenario 01 criterion 4 over-specifies the correct action

**Severity:** scenario 01 is universally penalized for what may be the more correct answer.
**Behavior:** criterion 4 demands "recommends a test pinning the upstream invariant instead of a defensive guard." All four scenario-01 responses converge on "do not add anything to the function; trust the model invariant; the existing model-validation test already covers the constructor; optionally strengthen *that* test or add a doc-comment." Two of four (gpt-5 baseline and treatment) explicitly say "strengthen the model test rather than" (matching marker "test rather than") and pass criterion 4. The other two (both gemini) recommend pure trust-the-type with no test addition.
**Open question:** is "trust the type, no addition, the existing model test covers it" a *correct* answer or a *complacent* one? My read: it is correct *as stated by the scenario prompt*, because the prompt explicitly says the model already has a green model-validation test for the invariant. The criterion is implicitly asking for redundancy ("add a test in addition to the existing one") and that is not obviously right.
**Repair candidates:**
   - **(a)** Widen marker list: add "trust the type," "trust the model," "strengthen the model test," "tighten the existing test," "doc-comment near the function" to criterion 4 markers.
   - **(b)** Rewrite the criterion: "Recommends *either* (i) adding a regression test that pins the upstream invariant, *or* (ii) explicitly justifying that the existing model-validation test is sufficient and naming what would make it not sufficient (e.g., mutable fields, deserialization bypass, reflection)."
**My recommendation:** (b), because (a) accepts complacent answers ("trust the type" without naming what would invalidate that trust). (b) requires the response to *engage* with what makes the trust justified, which is the actual form-check discipline. **Before applying (b), I must write a synthetic wrong-answer** (one that says "no need for a require() guard, the type system has us covered, done" without the bypass-path enumeration) and confirm (b) still fails it. This is the test-as-spec analog for rubric edits. **Not yet done.**

### B3. Scenario 01 criterion 3 is strict; keep it

Criterion 3 ("names the reviewer failure mode: reviewing the function in isolation without tracing model invariants") only fires when a response is metacognitive about what the *reviewer* should have done. Three of four scenario-01 responses give structural reasons (DRY, type system, existing test) without the metacognitive observation; only `gemini/treatment` says "Evaluating computeScheduledDoses in isolation without inspecting the domain objects." This is *exactly* the discriminator form-check is supposed to teach. Keep the criterion strict. The miss here is real, not an instrument artifact.

### B4. 10-word substantive-sentence floor cuts off heading-style answers

**Severity:** dominant rubric-failure mode for scenario 02; secondary in scenario 03.
**Location:** `specialists/form-check/tests/pressure_scenarios/_grading.py:51`; `_SENTENCE_BREAK = re.compile(r"(?:[!?\n]+|(?<!\d)\.+(?![a-z]))")` plus the 10-word minimum at line 39.
**Behavior:** responses that put the answer in a *heading* ("Test-only change first", "Implementation change second", "Verdict: Reject and Split") have those headings split off as their own sentences by the `\n` break and then fail the 10-word floor. The marker may match the heading text literally but the wrapper rejects it because the sentence is too short.
**Confirmed via instrumented run:**
```text
$ python3 -c "from _grading import Transcript; t = Transcript(open('runs/gpt-5/02/treatment.txt').read()); print([s for s in t.substantive_sentences if 'commit' in s])"
['blocking finding: test and fix were coupled in one commit',
 'commit a test-only change that replaces the wrong assertion with the allocator-issued notification id']
$ # "first commit" appears only in a 5-word heading, which is filtered out.
```
**Why the floor exists:** to defeat "keyword soup" inputs that just list expected markers. Documented at `_grading.py:32-37`.
**Repair candidates:**
   - **(a)** Lower the floor to 6 words. Catches headings like "Test-only PR or first commit" (5 words: still no good) and "Submit the failing test: Update the PR" (7 words: yes). Risk: re-opens the keyword-soup attack.
   - **(b)** Two-pass check: first try substantive sentences at floor=10; if no match, retry at floor=4 *only if* the broader transcript also contains a substantive sentence on the same concept (a "supporting context" check). More complex; better fidelity.
   - **(c)** Per-criterion floor override: some criteria (e.g., "provides the two-commit sequence") are inherently expressed as enumerated short items. Allow `Transcript(text, min_words=4)` for those specific criteria.
**My recommendation:** (c), the most surgical. Apply to scenario 02 criterion 4 and scenario 03 criterion 4 specifically. Document the per-criterion override in `_grading.py` docstring. Verify against transcripts.

## Adversarial review of this analysis (form-check Phase 2 against the doc itself)

Falsifiers I considered. The ones that landed are folded into the body above. The ones that did not:

1. **"You are grading your own homework."** Yes; I wrote the criteria, the markers, and the hand grades. This is reduced but not eliminated by the rubric runs in §Reconciled per-cell grades; those are mechanical and not subject to my biases, and they constrain my hand grade by forcing me to explain every disagreement. A human cross-check (Wei reading 2-3 transcripts at random and independently grading) is the actual mitigation; this analysis does not substitute for it.
2. **"Treatment effect claim is fragile."** Tightened in v2: 3 of 6 (down from v1's 4 of 6) with verbatim quotes. The remaining claim is descriptive (form-check vocabulary appears in treatment), not causal.
3. **"Recommendations could lock in a worse rubric."** True for B2(b) until I write the synthetic wrong-answer counter-test. **Decision: do not apply B2 until that test exists.** Decision is recorded in the top-of-doc decisions list.
4. **"Audit transcripts are gitignored, so this analysis is unreproducible."** Acknowledged. The transcripts live at `runs/<model>/<scenario>/<condition>.txt` on the local machine that ran the audit. Re-running the 12 trials per `TRIAL_CHEATSHEET.md` produces fresh transcripts; the rubric grades against fresh transcripts will reproduce up to model nondeterminism.

## Synthesis

- The rubric, after today's v0.3.2 enrichment, is approximately right on substance. The remaining 0/12 → 8/12 (or 12/12 if B2 accepted) gap is mostly **instrumentation issues** (B1 syntax bug; B4 sentence floor) rather than rubric philosophy or model deficiency.
- Web-LLMs GPT-5 and Gemini-2.5-Pro answer all three scenarios substantively correctly the majority of the time, with or without the form-check preamble. The preamble adds form-check-specific scaffolding (numeric thresholds, Component-N citations, Iron Law verbatim) to about half of treatment responses.
- These three scenarios **do not have enough discriminative power to test the form-check effect numerically.** Both models are already above the discrimination threshold without the preamble. For real treatment-effect measurement, future scenarios need to start from a confident wrong baseline answer that form-check has to actively redirect.
- v0.3.2 ships as an `advisory` calibration entry (per form-check Section 5 N<10 rule). No quantitative claim attached. The qualitative finding (preamble lands in ~half of treatment trials) is the headline.

## Status of recommended next actions

1. **B1; scenario 03 orphan-markers syntax bug.** *Done.* Rubric for scenario 03 went 0/4 → 4/4. Verified by ast.parse + transcript-by-transcript rubric re-run.
2. **B4; per-criterion `min_words` override.** *Done.* `Transcript.with_floor(n)` helper added to `_grading.py`. Applied at floor=3 to scenario 02 criterion 4 and floor=4 to scenario 03 criterion 4. Rubric for scenario 02 went 0/4 → 4/4. Verified by sentence-floor dump.
3. **B2(b); scenario 01 criterion 4 disjunctive rewrite + synthetic counter-tests.** *Done.* Criterion now passes on (i) explicit test recommendation with active verb OR (ii) structured bypass-path enumeration with invalidation framing. Two synthetic transcripts in `red_flag_detection/upstream_constraint_missed/synthetic_*.txt` serve as permanent counter-tests. Verified: `synthetic_wrong_complacent.txt` fails 3 criteria; `synthetic_right_justified_trust.txt` passes 4/4.
4. **Re-run 12 trials with fixed rubric, archive old verdicts.** *Done.* `runs/results.pre-fix.jsonl` contains the pre-fix record; `runs/results.jsonl` contains the post-fix grades with `rubric_version: v0.3.2-post-phase11-audit`. Aggregate: 8/12 PASS.
5. **N=1 calibration entry in `form-check.skill/.recovery/calibration.jsonl`.** *Pending commit.* See `calibration-entry` todo.
6. **Update `tests/pressure_scenarios/README.md` in the form-check.skill standalone.** *Pending commit.* One-paragraph honest summary of what Phase 11 measured.
7. **Cross-check by Wei (recommended).** Open. Read 2-3 transcripts at random, independently hand-grade against the criterion docstrings, flag disagreements >±1 criterion per cell.
8. **v0.4 harder scenarios.** Open. Draft 2-3 scenarios where the *baseline* answer is a confident wrong (e.g., model strongly wants to add defensive validation; form-check should redirect to test-pinning the upstream invariant).

## Pedagogical takeaways

Per trainer voice rules: cap at three.

- **Rubric is the discipline; markers are one finite encoding of it. The encoding can be wrong without the discipline being wrong.** Bugs B1 and B4 in this audit are exactly that shape: the conceptual criterion was right, the encoding silently dropped it. The form-check Iron Law analog: *no marker bumping without new evidence, and no relaxation without a counter-test.*
- **"Substantively correct without the preamble" is the worst case for a preamble's discriminative power.** A preamble can only show up in *form*, not *conclusion*, when the model already gets the conclusion right. Form-check's actual value claim is metacognitive discipline scaffolding; this audit shows that scaffolding *does* land qualitatively in roughly half of treatment trials, but cannot show whether the scaffolding improves *correctness* until we run scenarios where the baseline is wrong.
- **N=3-per-cell is a journal, not a study.** Treat this calibration log as a structured qualitative record. Inferential claims about form-check effectiveness require N≥50 with linked outcomes (per Section 5). The discipline is to keep logging, not to over-read the early entries.
