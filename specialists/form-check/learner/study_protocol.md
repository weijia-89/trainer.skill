---
type: learner-content
rubric_component: null
audience: developer 6-18 months into coding
companion_to: QUICKSTART.md, lessons/
---

# Study protocol — how to actually retain what's in this skill

The eight habits below come from cognitive-science research with **convergent, replicated evidence** that applies directly to learning to review and write software. Each habit has a citation, a software-specific mapping, and an instruction you can apply this week.

Read this *once* end-to-end. Then re-read the section that matches what you're trying to do. The retrieval prompts at the end of this file are designed to test whether the habits stuck.

---

## 1. Retrieval beats re-reading (the testing effect)

**Research.** Roediger & Karpicke (*Psychological Science* 2006); Karpicke & Blunt (*Science* 2011); Adesope, Trevisan & Sundararajan (*Review of Educational Research* 2017, meta-analysis k=118, g=0.61).

**The finding in plain language.** When you *try to remember* something, the act of trying — even if you fail — strengthens the memory more than re-reading the same material. Re-reading creates familiarity (which feels like learning) without actual recall ability.

**Mapping to this skill.** For each PR you review:

1. **Close the file.** Don't have `rubrics/confidence_score.md` open.
2. **Try to walk the 9-component rubric from memory.** Speak the components aloud or write them in a notebook. ("Code-read depth. Test verification. Hallucination check. Bug-class coverage. Adversarial pass. Reversibility. Doc accuracy. Blast radius. Threat model.")
3. **Now open the file.** Check your list. The components you missed are the ones you'll retain after this session — your brain is now primed to encode them.

**What this beats.** Re-reading the rubric every time. Five PRs in, you'll feel familiar with it but won't be able to recite it cold; *that's* the perception–reality gap that METR documented in seniors.

---

## 2. Spaced practice beats cramming (the spacing effect)

**Research.** Cepeda et al. (*Psychological Bulletin* 2006, meta-analysis k=839); Bahrick & Phelps (*JEP:LMC* 1987, 50-year Spanish-vocabulary retention with spacing).

**The finding in plain language.** Reviewing material once a day for a week beats reviewing it seven times in one sitting — by a large margin on delayed recall. Optimal interval between reviews is ~10–30% of the desired retention interval.

**Mapping.** After every PR, schedule four review touches:

| When | What you do |
|---|---|
| Same day, end of work | 2-minute recap: what was the PR, what tier, which floor walked, any surprises? |
| +1 day | Re-walk the rubric (from memory) on the *same* PR. Note any gaps. |
| +3 days | Spot-check: which component would catch a similar bug? |
| +1 week | Quiz yourself on what you'd do differently. |
| +1 month | Add the PR to your "case library" if it taught you something. |

If you can't do the full cadence, the *first* and *fourth* touches matter most. Skipping the in-between still beats skipping all spaced repetition.

**What this beats.** "I'll learn it as I go." You won't. Ebbinghaus measured the forgetting curve in 1885; replicated by Murre & Dros 2015. Without spaced repetition, you forget ~70% within 24 hours.

---

## 3. Interleave similar topics (the discrimination hypothesis)

**Research.** Rohrer & Taylor 2007 (*Instructional Science*); Rohrer 2012 (`ROHRER-2012` `[T1-verified]`); Taylor & Rohrer 2010; Kang 2016 review; Carvalho & Goldstone 2015 (`CARVALHO-GOLDSTONE-2015` `[T1-verified]`).

**The finding in plain language.** Mixing similar topics — math problem types, plant species, painting styles — produces better discrimination than studying them in blocks. The discrimination *is* the harder skill.

**Boundary conditions** (load-bearing — interleaving is NOT a generic "always mix" recommendation):

- **Works** when the concepts are **related-but-distinct** (e.g. similar math problem types; similar bug classes). The mixing forces active discrimination.
- **Does not work** for genuinely unrelated concepts (e.g. mixing supply-chain audit with React component design). Without shared structural features, mixing just produces interference, not discrimination.
- **Does not work** for true beginners with no prior schema for any of the topics — interleaving relies on the learner being able to *notice* the differences. If the learner doesn't yet have schemas for either topic, blocked practice first, then interleave.
- **Empirical anchor**: Carvalho & Goldstone 2015 demonstrated interleaving's effect depends on category similarity; high-similarity categories benefit, low-similarity categories may not.

**Mapping.** When you're learning the difference between hallucination-check, supply-chain audit, and test-verification: these are related-but-distinct (all are "things to verify before merge"), so interleave them — do 3 of each, mixed. The pattern-discrimination ("this PR needs *which* check?") is the actual skill.

When you're learning hallucination-check vs. accessibility audit vs. tax-domain modeling: these are genuinely unrelated; do not interleave. Block first, build the schema for each, then interleave only the related-but-distinct subset.

For the cautionary tales: `learner/cautionary_tales.md` is *already* interleaved within the related-but-distinct family of "AI-assisted-coding incidents" — supply chain, productivity gap, BOLA, defaults, transitive deps, mixed deliberately. Read it in order, not by category.

**What this beats.** "I'll master one topic before moving to the next." For related-but-distinct topics, that builds depth without discrimination. **What this does *not* beat:** the case where topics are unrelated or the learner has zero prior schema; in that case, blocked practice is correct.

---

## 4. Worked examples with fading (cognitive load theory)

**Research.** Sweller & Cooper 1985 (`SWELLER-COOPER-1985` `[T1-replicated]`); Atkinson, Renkl & Merrill 2000 meta-analysis (`ATKINSON-RENKL-MERRILL-2000` `[T1-replicated]`); van Merriënboer & Sweller 2005; **Kirschner, Sweller & Clark 2006** (`KIRSCHNER-SWELLER-CLARK-2006` `[T1-replicated]`, *Educational Psychologist*, 4,000+ citations: "Why Minimal Guidance During Instruction Does Not Work"); Margulieux & Catrambone 2016 (`MARGULIEUX-CATRAMBONE-2016` — programming-specific subgoal labeling).

**The finding in plain language.** Beginners with no schema for a problem-space are overwhelmed by problem-solving from scratch. Show them a *complete* solution first; then a partial one to complete; then less and less scaffolding. The "fading" sequence builds the schema. **For novices, unguided exploration / discovery learning underperforms direct instruction with worked examples** — this is a well-established negative finding (Kirschner-Sweller-Clark), not a stylistic preference.

**Programming-specific extension — subgoal labels.** When you study a worked code example, label each step with its *purpose* ("validate input shape," "look up by primary key," "format result"), not its *action* ("call `assert isinstance`," "query DB," "render template"). Subgoal labels improve transfer to novel programming problems (`MARGULIEUX-CATRAMBONE-2016`, replicated by `JOENTAUSTA-HELLAS-2022`). When you read `learner/first_pr_walkthrough.md`, write the purpose-labels for each step in the margin.

**Mapping.** `learner/first_pr_walkthrough.md` is a complete worked example. To get value:

1. **First pass:** read it once, follow the reasoning.
2. **Second pass:** re-read with the last step blank — predict what the author did, then check.
3. **Third pass:** start with step 5 blank, then step 4, then step 3.
4. **Final stage:** do an analogous PR on your own code, narrating the same steps in `learnings.md`.

**What this beats.** "Just dive in and figure it out." For schemas you don't have, this overloads working memory and prevents schema-building. Worked examples + fading is the *most evidence-backed* learning sequence in cognitive science.

---

## 5. Self-explanation prompts (the Chi effect)

**Research.** Chi, de Leeuw, Chiu & LaVancher 1994 (`CHI-1994` `[T1-replicated]`, 22% gain over non-explainers); **Bisra, Liu, Nesbit, Salimi & Winne 2018 meta-analysis** (`BISRA-2018` `[T1-replicated]`, *Educational Psychology Review* 30(3): g=0.55, k=20 moderator variables, replaces the older Wylie & Chi 2014 chapter as load-bearing citation). Adjacent: Slamecka & Graf 1978 generation effect (`SLAMECKA-GRAF-1978`).

**The finding in plain language.** When you force yourself to articulate *why* something works, you discover gaps in your understanding that re-reading would never expose.

**Mapping.** For every PR you review, before clicking approve/comment, write the answers to *three* self-explanation prompts:

1. **"Why this change and not the obvious alternative?"** (Names the choice the author made and the trade-off it implies.)
2. **"What does this code assume that, if violated, would break it?"** (Names the failure mode.)
3. **"If I had to teach a junior how to maintain this in a year, what would I say?"** (Surfaces hidden complexity.)

Three sentences each. Write them in `learnings.md` or in the PR description before approval. The writing *is* the learning.

**What this beats.** Reviewing PRs by clicking through and skimming. You will retain *none* of what you reviewed. Self-explanation forces encoding.

---

## 6. Productive failure (Kapur)

**Research.** Kapur 2008 (`KAPUR-2008` `[T1-verified]`, *Cognitive Science*); Kapur 2014 (*Educational Psychologist*); Loibl, Roll & Rummel 2017 meta-analysis (`LOIBL-ROLL-RUMMEL-2017` `[T1-replicated]`); **Sinha & Kapur 2021** (`SINHA-KAPUR-2021` `[T1-replicated]`, *Review of Educational Research* 91(5)) — the load-bearing meta-analysis that identifies *boundary conditions*.

**The finding in plain language.** Trying to solve a problem *unsuccessfully* before being shown the canonical solution produces better transfer than being shown the solution first. The struggle activates relevant prior knowledge and exposes gaps that prime the brain for the instruction.

**Boundary conditions** (load-bearing — productive failure is NOT a generic "always struggle first" recommendation):

Per `SINHA-KAPUR-2021`, productive failure works only when:

1. **Prior knowledge floor** — the learner has *some* relevant prior knowledge to activate. With zero prior knowledge, struggle is just frustration; direct instruction first (per `KIRSCHNER-SWELLER-CLARK-2006`).
2. **Problem affordances** — the problem is designed so that the natural failure modes *surface the to-be-learned concept*. A random hard problem is just hard; a *productive* problem is engineered to fail in instructive ways.
3. **Consolidating instructional follow-up** — the struggle is followed by canonical instruction that connects the failure to the principle. Without follow-up, you get failure without the productive.

If any condition is missing, do not productive-fail; use direct instruction with worked examples.

**Mapping.** For any change in your tier-classification (you have prior knowledge, the rubric has structured affordances, the canonical answer is in `rubrics/confidence_score.md` — all three conditions hold):

1. **First**, write down what *you* think the right approach is. Score your own change against your guess of the rubric.
2. **Then** open the rubric. Compute the actual score.
3. **The gap is where learning lives.** Note it in `learnings.md`.

For new topics (you've never heard of STRIDE, never used mutation testing): only productive-fail *after* you've encountered the concept once via direct instruction (a worked example, a definition). For pure first-encounter, the boundary conditions don't hold — read first, apply second.

**What this beats.** "Read the rubric, then apply it" *for cases where the boundary conditions hold*. **What this does not beat:** first-encounter learning of a wholly novel concept, or struggle without follow-up.

---

## 7. Calibration training (the metacognitive habit)

**Research.** Lichtenstein, Fischhoff & Phillips 1982 (`LICHTENSTEIN-1982` `[T1-replicated]`, foundational); Koriat & Bjork 2005 (`KORIAT-BJORK-2005` `[T1-replicated]`, "foresight bias"). **Note on Dunning-Kruger 1999:** Gignac & Zajenkowski 2020 (*Intelligence*, peer-reviewed) and Gignac 2024 demonstrate the original D-K effect is *mostly a statistical artefact* of regression-to-mean + better-than-average effect. The phenomenon of metacognitive miscalibration is real and well-evidenced; the D-K specific framing is contested. **This skill does not anchor on D-K.**

**The finding in plain language.** Almost everyone over-predicts their own future performance — especially after recent study (which produces false familiarity). Calibration training — *predict, measure, observe the gap* — gradually closes the prediction error.

**This is the skill that distinguishes senior from junior engineers in practice.** A senior is not necessarily faster than a junior at solving any one problem; they are dramatically better at predicting *which* problems will be hard.

**Mapping.** Three concrete calibrations to track:

| Prediction | Measurement | Habit |
|---|---|---|
| "How many tests will pass after this change?" | Run the suite | Note the gap |
| "What mutation score will this code earn?" | Run mutation testing | Note the gap |
| "How big will the resulting diff be (lines)?" | Read the diff | Note the gap |
| "How confident am I in this change (0–100)?" | Compute the rubric | Note the gap |

Keep a running log. After ~20 PRs, look at your average gap. The trend should be *down*. If it isn't, you're not calibrating — you're just repeating predictions without updating.

**What this beats.** "I feel good about this PR." Self-assessed software-engineering productivity is systematically miscalibrated (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, both `[T1-replicated]`). One preliminary RCT consistent with this — `METR-2025` `[T1-verified, n=16]` — measured experienced devs feeling +20% faster while being measurably −19% slower; METR's own follow-up (Feb 2026) was redesigned for unreliability, so the magnitude is preliminary. The general phenomenon (perception ≠ measurement) is the actionable signal. The feeling is unreliable. The log is reliable.

---

## 8. Schema acquisition through varied examples

**Research.** Gick & Holyoak (*Cognitive Psychology* 1983, the radiation-problem study showing transfer requires varied examples + an explicit comparison hint); Goldwater & Schalk (2016 STEM-transfer review).

**The finding in plain language.** A single example produces a *surface* memory. Multiple examples with varied surface features force you to abstract the *deep* structure — that's schema acquisition. Without that, transfer is "near-only" (the new problem must look almost identical).

**Mapping.** When you study a pattern (say, BOLA — broken object-level authorization):

1. Read at least **three** incident reports of BOLA from different domains (a fintech, a healthcare app, a social-media platform).
2. List what they have in **common** at the deep level (the auth-vs-authz confusion, the URL-id-substitution attack).
3. List what they have in **different** at the surface level (different frameworks, different data, different impact).
4. State the **deep schema** in one sentence.

Now the schema can fire on a *new* PR you've never seen, even in a domain you don't work in. That's transfer.

**What this beats.** Reading one BOLA case and thinking you've got it. You've got the *surface*, not the schema. The Gick & Holyoak 1983 result was specifically about this: subjects who'd read one isomorphic problem failed to transfer; subjects who'd read two with a comparison hint succeeded.

---

## 9. Direct instruction for novices (the anti-discovery finding)

**Research.** Kirschner, Sweller & Clark 2006 (`KIRSCHNER-SWELLER-CLARK-2006` `[T1-replicated]`, *Educational Psychologist* 41(2), 4,000+ citations: "Why Minimal Guidance During Instruction Does Not Work"). Adjacent: `SWELLER-COOPER-1985`, `ATKINSON-RENKL-MERRILL-2000`.

**The finding in plain language.** For learners without a strong schema in the domain, **unguided exploration / discovery / problem-based learning underperforms direct instruction with worked examples.** This is not a stylistic preference. It is a robust empirical finding across domains, replicated for decades, mechanistically grounded in cognitive load theory.

**Why this is in this skill.** A common AI-coaching mistake is "just figure it out, you'll learn faster." For novices, that's wrong. The rubric, the worked examples in `learner/lessons/`, and the floors are *direct instruction*. Walk them. Don't replace them with "let me just try things."

**Mapping.** When you encounter a new concept (STRIDE, mutation testing, idempotency keys, expand-contract migration):

1. Read the canonical worked example first (the lesson, the docs, the rubric component).
2. Apply it to a small concrete case.
3. *Then* productive-fail on a harder case (per Habit 6, after the boundary conditions hold).

Do not invert this order for a wholly novel concept. The "just dive in" approach is the unguided exploration that the literature consistently shows produces *less* learning than guided approaches for novices.

**Boundary condition (when this advice softens):** for learners with strong existing schemas in adjacent domains, guided discovery can work — the schemas reduce cognitive load. The audience for this skill (6–18 months coding) does *not* yet have those schemas in most areas of the rubric.

---

## The pedagogy paradox — and how to keep the AI from closing it for you

This skill demands retrieval practice (Habit 1), self-explanation (Habit 5), productive failure with boundary conditions (Habit 6), calibration (Habit 7), and direct instruction first for novices (Habit 9). All nine habits assume **you, the human, do the cognitive work.**

The paradox: you are using an AI assistant. The AI will *cheerfully* recall the rubric for you, generate the self-explanation, predict the test-suite result, score the change. If you let it, **the AI's cognition replaces yours**, and the *learning conditions disappear*. You acquire familiarity (you saw the answer), not capability (you produced the answer).

This is not hypothetical. It is the central design failure mode of every "learn with AI" workflow that doesn't address the paradox directly. Acknowledge it; design around it.

### The protocol — when the AI is loaded

When you are working a PR with an AI assistant active, before you accept any AI-produced answer to a *learning-relevant* question:

1. **Predict first, then reveal.** State your own answer in writing — even one sentence. Then ask the AI. The gap between your prediction and the AI's answer is the calibration signal (Habit 7). If you skip the prediction, you skip the learning.
2. **Generate first, then verify.** When self-explaining (Habit 5), write the three sentences yourself before asking the AI to critique them. Reverse this order and the AI generates; you read; you encode nothing.
3. **Recall first, then look up.** When the AI offers to walk through the rubric, **decline until you have walked it from memory.** Then use the AI as a checker, not a recaller.
4. **Productive-fail first (when boundary conditions hold per Habit 6), then read.** When you can predict the type of failure, predict it. Then ask the AI / read the canonical answer. Compare.

**The rule:** the AI is your *checker* on learning-relevant tasks, never your *recaller* or *generator*. If you find yourself skipping the prediction-first step "to save time," you are also skipping the encoding. Token cost is not the binding constraint; *your future capability* is.

### The protocol — when no AI is loaded ("study mode")

Some tasks merit no-AI sessions:

- **Spaced-review touches** (Habit 2 cadence): every +1 day / +3 day / +1 week / +1 month review of a past PR. **Do these without the AI loaded.** The retrieval practice is the point.
- **Periodic rubric recall.** Once a month: close every reference, recite the 9 components and weights. Then check.
- **Calibration log entries.** Write the predicted-vs-actual *before* asking the AI to compute the actual.

If your harness supports a "study mode" flag (no AI / read-only AI), use it for these. If not, force the protocol manually: close the AI panel, do the retrieval, only then re-open.

### How to know you're cognitive-offloading

Red flags in your own behavior:

- "I'll just have the AI recall the rubric this once." (You won't ever recall it cold.)
- "The AI's self-explanation is clearer than mine, so I'll use that." (You haven't self-explained at all.)
- "The AI predicted a 92, that's probably right." (Your prediction was the calibration signal; you skipped it.)
- "I don't need the spaced-review on this PR; the AI remembers it." (The AI's memory is not your memory.)

Each red flag means: you've outsourced the cognitive step the habit was designed to train. Stop, do the step yourself, then resume.

### The bottom line

The skill is designed for *humans who use AI assistants*, not for *AI assistants who happen to have humans nearby*. If you let the AI do the retrieval, self-explanation, prediction, or calibration, the skill stops working. The harness can't enforce this; you have to.

This paradox is not unique to coding. The same design failure shows up in language learning with translation tools, in math learning with computer-algebra systems, in writing with autocomplete. The pedagogy literature is consistent: **the cognitive work the learner does is the cognitive work the learner learns from.** Outsource it and you outsource the learning.

---

## What does NOT work (the literature is clear)

Three things commonly claimed in coding pedagogy that the research doesn't support — don't waste your study time:

- **Matching to learning styles** (visual / auditory / kinesthetic). `PASHLER-2008` reviewed the entire literature: no evidence that matching instruction to claimed style improves outcomes. The myth persists because *learners self-report* preferences. Outcomes don't follow.
- **"Just write code, you'll learn"** without structured reading. Vihavainen et al. 2014: *reading code* is at least as valuable as writing it; structured curricula with worked examples outperform pure project-based learning for beginners. See `KIRSCHNER-SWELLER-CLARK-2006` for the broader anti-discovery finding.
- **Immersion alone** without retrieval practice. Years-on-the-job produces a senior-engineer *feel*. The feel is partly real schema and partly false familiarity (the metacognitive-miscalibration finding from Habit 7 applies). Calibration training is the corrective.
- **Dunning-Kruger as a load-bearing model** of novice overconfidence. The original D-K effect is mostly a statistical artefact (`GIGNAC-ZAJENKOWSKI-2020`, `GIGNAC-2024`). The *phenomenon* of metacognitive miscalibration is well-evidenced via `LICHTENSTEIN-1982` and `KORIAT-BJORK-2005`; do not anchor reasoning on D-K specifically.

---

## Templates

### Per-PR `learnings.md` template

```markdown
# Learnings — [PR ID / change name] — [date]

## What I shipped
(One sentence)

## Tier
vibe-safe / vibe-careful / vibe-dangerous

## Floor I walked
1 / 2 / 3 — list which steps I actually did vs which I skipped

## Self-explanation (three sentences)
- Why this change and not the obvious alternative?
- What does this code assume that, if violated, would break it?
- What would I say to a junior who has to maintain this in a year?

## Calibrations
| Predicted | Actual | Gap |
|---|---|---|
| Tests passing | ... | ... | ... |
| Mutation score | ... | ... | ... |
| Diff size (lines) | ... | ... | ... |
| Confidence (0–100) | ... | ... | ... |

## Surprise / gotcha
(If anything surprised me — write it down. The surprise is the learning signal.)

## Spaced-review schedule
- [ ] +1 day: re-walk rubric on this PR
- [ ] +3 days: spot-check ("which component would catch a similar bug?")
- [ ] +1 week: quiz myself ("what would I do differently?")
- [ ] +1 month: promote to case library if relevant
```

### Spaced-review schedule template

For each PR, set four calendar reminders:

- **+1 day, 5 min**: re-walk rubric from memory; check `learnings.md`
- **+3 days, 5 min**: spot-check related concept
- **+1 week, 10 min**: full quiz; revise `learnings.md`
- **+1 month, 5 min**: case-library promotion decision

If you don't use a calendar tool, write the next-review date at the top of `learnings.md`.

### Calibration-log running totals

Once a month, look at your last 20 PRs and compute:

- **Mean absolute gap** for each predicted variable (lower is better).
- **Trend** (is it going down? if not, why not?).
- **Worst prediction**: which PR had the largest gap? What was the lesson?

---

## Retrieval prompts for this file

To test whether *this* file stuck, close it and answer (write the answers, then re-open):

1. Name the nine habits. (Hint: they map to *retrieval, spacing, interleaving, worked examples, self-explanation, productive failure, calibration, varied schemas, direct instruction for novices*.)
2. What's the established phenomenon behind self-reported productivity miscalibration (with citations) and which preliminary RCT is one example of it (with caveats)?
3. Why is "read the rubric, then apply it" *worse* than "guess first, then read" — and what are the **boundary conditions** under which "read first" is actually correct?
4. What does Pashler et al. (2008) say about learning styles?
5. What's the difference between near-transfer and far-transfer, and what does schema acquisition do for far-transfer?
6. Why is calibration training the most senior-engineer-distinguishing habit?
7. Name the **three boundary conditions** for productive failure (per `SINHA-KAPUR-2021`).
8. When does interleaving *not* work?
9. Why is direct instruction with worked examples *better* than discovery learning for novices, and what's the citation?
10. Why does this skill not anchor on Dunning-Kruger, even though novice overconfidence is real?

If you missed more than two, re-read the section. Then come back in three days.
