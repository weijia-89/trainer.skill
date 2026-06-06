# Trainer — epistemic layers & code-adjacent eval routing

Palamedes stays **non-code research**. This doc is trainer-owned routing — not loaded by Palamedes.

---

## §TRIGGER (load gate)

Load this file **iff** any:

1. User task mixes Palamedes-style **research** with **automated eval metrics**, **CI regression gates**, or **release** decisions.
2. User asks which skill owns research vs eval vs code QA, or names "layer" / "L1 L2 L3" in that sense.
3. User signal matches **Trainer dispatch** below (eval harness, wire CI, compare eval frameworks, interview prep about eval metrics).

**Do not load** when task is pure code review / refactor with no eval or research framing → **form-check** / **review-rigor** only.

---

## Three layers (deterministic assignment)

| Layer | Question it answers | Canonical skill / owner | Forbidden substitution |
|-------|---------------------|-------------------------|-------------------------|
| **L1 Decision** | Should we believe / ship / publish this conclusion? | **palamedes** (research loop) | Metric score alone, CI green, vibe |
| **L2 Trace QA** | Did this RAG/LLM **run** behave (retrieval vs generation)? | **Project harness** (DeepEval, Promptfoo, repo eval scripts) + **form-check** for claims | Palamedes loop inside CI |
| **L3 Structured truth** | Do schemas, tests, SQL, Playwright prove invariants? | **review-rigor**, **form-check**, repo tests | LLM-judge alone |

**Routing rule TR-1:** Classify the user’s **immediate task** to exactly **one primary layer**. Secondary layers may be cited or required as proof, but must **not** co-drive the primary deliverable.

```
IF task = lit review / fact-check / strategy memo / compare vendors (no repo eval)
  → primary L1 (palamedes); defer L2/L3

IF task = eval harness / CI metric / regression gate / product eval-lab QA
  → primary L2 (trace QA + harness)
  → secondary L3 when merge/release needs test or schema proof (review-rigor / repo CI)
  → palamedes only for *research about* eval (methodology questions), not harness config

IF task = recruiter screen / interview prep about eval
  → primary L1 framing; L2 one-liner only; no harness config in palamedes session
```

---

## Trainer dispatch (when user asks “which skill?”)

| User signal | Route |
|-------------|-------|
| "How does [eval framework] work?" / "compare eval frameworks" | **palamedes** + `~/Projects/palamedes/skill/references/rag-eval-literacy.md` |
| "Wire eval into CI" / "fix regression gate" | **form-check** + repo; **not** palamedes |
| "Is this PR ready?" / code review | **form-check** / **review-rigor** |
| "Research company / paper / policy" | **palamedes** |
| Parallel agents on same repo | **superset** + layer tag per agent |

---

## Eval-corpus tiering (code path — **not** Palamedes)

User directive: Palamedes does **not** own test-case tiers. When trainer sees **release gates on automated eval**, apply:

| Tier | Name | Gate rule |
|------|------|-----------|
| **E-T1** | Canary | May block merge/release |
| **E-T2** | Stress / adversarial | Failures → investigate; do not alone block unless promoted to E-T1 |
| **E-T3** | Exploratory | Log only; **forbidden** as sole ship evidence |

**Implementation plan (trainer → form-check / project, not palamedes skill body):**

1. Document E-T1/E-T2/E-T3 in repo `README` or eval harness doc (e.g. `eval/README.md`).
2. CI config references **only** E-T1 paths for hard fail.
3. PR template: "Which tier changed?"
4. Interview prep may **describe** tiers without Palamedes loading them.

---

## Coached pushback triggers

- User runs Palamedes loop to replace missing CI eval → push back; route L2.
- User treats automated faithfulness score as clinical safety → push back; cite J-4 in `rag-eval-literacy.md`.
- User collapses multi-metric dashboard to one green badge → push back; cite MM-1 in `rag-eval-literacy.md`.

Log coached override per trainer SKILL if user insists.

---

## Cross-links

- Palamedes eval literacy: `~/Projects/palamedes/skill/references/rag-eval-literacy.md`
- Palamedes architecture (trainer routing summary): `~/Projects/palamedes/docs/ARCHITECTURE.md`
- Gym: **form-check** (eval claims), **gymbuddy** (over-trusting judge scores)
