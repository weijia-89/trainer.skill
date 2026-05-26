---
name: form-check
description: |
  Use when planning a new app, reviewing a code change, hardening before launch, or adversarially reviewing existing code. Symptoms: AI invents APIs or package names, large diff without tests, irreversible operations suggested, secrets near staging, deletion paths, prompt injection in input, "is this ready to ship," tier-classification needed.
type: project-skill
version: 3.1.0
authors: Wei Jia (1.0, 2026-04); rewrite 2026-05-14; v3 evidence-base audit + Iron Law layering 2026-05-16; v3.1 Phase 9 token trim 2026-05-16
license: MIT
required_tools: [file_read, grep]
recommended_tools: [shell, git, web_search]
optional_tools: [browser]
composes: []
---

# form-check, someone watches one rep and tells you what's off

```
IRON LAW: NO SHIPPING WITHOUT TIER-FLOOR SCORE *AND* PER-COMPONENT MINIMA MET.
A HEADLINE PASS WITH A FAILED MINIMUM IS A FAIL.
```

Violating the letter of this rule is violating the spirit of this rule. "The headline is 92, only Hallucination is at 65, but I'm sure those imports are fine" is the rationalization that ships malicious dependencies. The minima are the floor; they exist precisely because a single weak component is the actual failure mode.

## Red Flags. STOP and re-score

If any of these thoughts is in your head:

- "Let me re-score, I'm sure I missed credit on component X."
- "It's 79 vibe-safe and I'm just one point off, that's fine."
- "I'll skip the calibration log entry this time."
- "The minima are too strict for this kind of change."
- "Pure refactor. I'll relax the threshold without checking the behavior-preservation gate."
- "This change feels safe, the score isn't representative."
- "I've shipped changes like this before without scoring."

Each red flag means: stop. The score is the discipline; rationalizing past it is what the discipline exists to prevent. **No score-bumping without new evidence.** A re-score on the same inputs is invalid.

## Rationalizations, what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "Per-component minima are too strict, headline is enough" | Headline ≥95 with Hallucination=60 ships malicious imports. The minima are the floor for a reason. |
| "I'll log the calibration entry later" | Later is never. Calibration without logging is just opinion. |
| "The threshold numbers are arbitrary anyway" | They are tagged `(uncalibrated)` until N≥50, see §5. **The ordering** (dangerous > careful > safe) is principled; the exact thresholds are operator wisdom awaiting data. The discipline is still the discipline. |
| "Pure refactor, no behavior change, so the relaxed threshold applies" | Only if a behavior-preservation check (golden / characterization / mutation-equivalent) actually passes. "Trust me, no behavior changed" is not a check. |
| "I scored this two PRs ago, the score still stands" | The score is per-change. Re-score. |
| "Tier-floor is the cap, I just need to clear it" | The minima are independent. Headline-floor AND minima-floor. Both. |

## Keywords for discovery

For trigger-keyword indexing: plan a new app, design an architecture, code review, adversarial review, refactor, ship it, launch ready, vibe coding, vibe-safe, vibe-dangerous, AI guardrails, what's the stack for, ADR, write tests for, confidence score, are we ready for prod, harden this, check for bug classes, regression risk, threat model, OWASP review, supply chain audit, fitness functions, deprecation policy, multi-language tooling, model invents APIs, package names look off, large diff with no tests, irreversible op suggested, secrets near to staging, deletion paths, prompt injection in input.

## Scope

Posture: senior engineer + tech lead planning new apps and reviewing existing code. Optimize for **beginner-friendliness, maintainability, extensibility**. Favor **boring technology**. Default-anti-enterprise (refuses microservices / k8s / event bus / CQRS / "scalable" without named forcing constraint); the `scale-up/` annex activates only when a forcing-constraint ADR is on record.

This skill is a **review/planning skill, not a code generator**. It guides agents that write code; it does not write code itself.

## Onboarding paths

File is senior-engineer voice: terse, normative, jargon-dense. If that fits, read straight through. If 6–18 months into coding, or you want a coaching/mentor presentation of the same content, take the learner track. Whichever path you take, keep `learner/study_protocol.md` close (the rest will not stick without it):

- **First-time read:** `learner/QUICKSTART.md` (glossary + 3-question tier classifier + safety floors).
- **Token-leak prevention** (highest single-stakes setup, 15 min, **non-optional**, senior engineers re-read after any near-miss; read before any code that touches an API token): `learner/token_handling_primer.md`.
- **Real incidents that motivate the floors:** `learner/cautionary_tales.md` (Replit, Shai-Hulud, slopsquatting, Lovable BOLA, METR perception gap, low-code default-exposure, left-pad).
- **Worked first PR, end-to-end:** `learner/first_pr_walkthrough.md`.
- **One lesson per rubric component:** `learner/lessons/` (start with `learner/lessons/03_hallucination_check.md`).
- **Retention pedagogy** to retain what's here, grounded in cognitive science (retrieval practice, spacing, calibration, productive failure, worked examples + fading, self-explanation, varied schemas): *second*-most non-optional, this is how the rest sticks: `learner/study_protocol.md`.
- **How learner mode is configured:** `learner/MODE_CONFIG.md`.

## How to invoke

Declare engagement type; the skill routes to leaf content. Always: read this file (posture) → `checklists/INDEX.md` (routing) → leaf. Cite primary sources via tags (`references/notes.md`). Apply Section 5 before declaring any change done.

- **plan-new-app** → `templates/CLAUDE.md_scaffold.md` + `rubrics/stack_decision.md` + `checklists/preflight_10q.md`
- **code-review / adversarial-review** → `checklists/INDEX.md`
- **refactor-prep** → `rubrics/confidence_score.md` + `checklists/smell_catalog.md`
- **harden** → `checklists/threat_model_stride.md` + `checklists/owasp_*_top10.md` + `checklists/supply_chain_slsa.md`
- **deprecate** → `checklists/deprecation_policy.md`

## Section 1. Vibe-coding guardrails (non-negotiable)

User-supplied rules, kept verbatim and load-bearing:

- **Every plan must specify** what the human reviews in full vs what AI can ship unread.
- **Flag any "review gate":** irreversible operations (DB migrations, secrets, production writes, external API calls with side effects, file deletes) **must be human-approved**.
- **Test-as-spec:** write test signatures/examples *before* asking AI to implement. *(Empirical caveat: TDD evidence in software engineering is **mixed**: `RAFIQUE-MISIC-2013` meta-analysis k=27 found small-to-moderate quality effect with high variability; `KOLLANUS-2010` mixed-evidence review. Treat test-as-spec as a discipline-shaping default with operator-wisdom backing, not as a proven productivity lever. The discipline matters because it keeps the spec falsifiable; the productivity claim is unsupported.)*
- **Distinguish vibe-safe** (UI tweaks, scaffolding, one-off scripts, internal tools) **from vibe-dangerous** (auth, payments, data migrations, security-sensitive logic).
- **For vibe-dangerous work:** require human-written tests, human-read diffs, staged rollout.

**Other software-engineering practices and their evidence (cite when invoking):**

- **Code review**, strong defect-detection evidence (`BACCHELLI-BIRD-2013` `[T1-replicated]`, `COHEN-2010`). Use modern lightweight code review.
- **Mutation testing**, catches real bugs at scale when applied with arid-mutant filtering (`PETROVIC-2018` Google ICSE). Higher-evidence than TDD.
- **Static analysis (lightweight)**, strong empirical basis (`BELLER-2016`).
- **Pair programming**: `HANNAY-2009` meta-analysis: small positive on quality, medium positive on duration, **large negative on effort** (i.e., person-hours roughly double). Qualifies any "always pair" claim. Pair on vibe-dangerous, not as a default.

Reinforced by 2025–2026 evidence (`references/notes.md`; the METR 2025 + 2026 self-redesign is the live caveat):

- **Metacognitive miscalibration is established** as a phenomenon (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, both `[T1-replicated]`); the metacognitive-miscalibration framing is the actionable one. One preliminary RCT consistent: `METR-2025` `[T1-verified, n=16, replication=METR-self-failed]`. AI-allowed condition −19% slower while devs perceived +20% speedup; METR redesigned the follow-up experiment (Feb 2026) for unreliable data, hence the caveats. **Take perception ≠ measurement as the general signal; the magnitude is not load-bearing; do not generalize to junior devs, novel domains, or well-defined tasks.**
- **DORA 2025** (`DORA-2025` `[T1-verified, survey-not-RCT]`): AI as amplifier across 7 maturity profiles, ~5,000 respondents, self-assessed delivery practices. Survey self-report, plausible but **not causally established**. DORA-metrics evidence (deployment frequency, lead time, MTTR, change failure rate) is solid; cite separately from the AI-amplifier claim.
- **SLOP-arXiv (Spracklen et al., USENIX 2025)**: LLMs hallucinate package names at **5.2% commercial / 21.7% OSS-model** rates when asked to write code. Threat chain: hallucinated name × attacker registers × dev copy-pastes AI output without verifying. **Verify every new import** (registry, author, first-seen date).
- **Shai-Hulud chronology** (`WIZ-SHAIHULUD-1`/`-2`/`-3`, `CISA-NPM-2025`), current supply-chain attack model: Sept 15 2025 (npm worm, ~500 pkgs) → Nov 21–23 2025 (2.0, 25k+ repos) → May 11 2026 (Mini, cross-ecosystem npm + PyPI). Pattern: post-install scripts exfil tokens to public GitHub repos. **Shared CI tokens are a single point of failure.**
- **Replit incident** (`REPLIT-FORTUNE`, `AIID-1152`): July 18 2025; agent deleted production DB during code freeze; CEO apologized. **Agents will run destructive ops without gates.**
- **Vibe-coding vulnerability pattern** (`WIRED-VIBE`, `LOVABLE-REGISTER`, `LOVABLE-CRISIS`): RedAccess identified ~5,000 vulnerable apps across Lovable / Replit / Base44 / Netlify; `CVE-2025-48757` covers the BOLA-on-AI-generated-code class; Lovable had 3 documented 2026 incidents. **Bug-bounty closures predicted future incidents** (security disclosure programs are themselves a vibe-safety surface).
- **`GITCLEAR-2025`** `[T2-vendor, COI:GitClear, unreplicated]`: vendor self-published code-quality report, copy-paste rising, refactoring shrinking, churn-within-2-weeks growing. Illustrative trend, not established quantitative evidence. Corroborate with `ACM-COPILOT-CORRECT` (correctness; T1) and `ACM-COPILOT-SEC` + `MAJDINASAB-2024` (cross-replicated T1).

## Section 2. Stack decision rule (with cites)

State **chosen + rejected alternative + 1-sentence why each**, anchored to a citation or explicitly tagged `[normative]`. Below: chosen + rejected + 1-line why each.

| Context | Default | Rejected alt | Why default | Anchor |
|---|---|---|---|---|
| One-person or JS-comfortable team | TS everywhere (Next.js App Router + Drizzle + Postgres via Neon/Supabase + Tailwind) | Python full-stack | Single language, single deploy, type-safety end-to-end | `[normative]` |
| Python-comfortable, data/ML-adjacent | Python + FastAPI + Postgres + Next.js (web UI) | Django monolith | FastAPI plays nicer with async + Pydantic v2 contracts; Django-Ninja closes the gap if Django ecosystem locked in | `[normative]` |
| Single binary / CLI | Go (stdlib + chi or cobra) or Rust (clap) | each other | Go: faster onboarding, stdlib enough; Rust: when memory/perf budget is the spec | `[normative]` |
| Forms-heavy CRUD, regulated, "boring web app" | Rails 8 with Solid stack OR Django | each other | Rails: Solid Queue/Cache/Cable removed Redis dep; Django: stronger admin and ORM ecosystem | `[normative]` |
| **Enterprise greenfield, JVM org, regulated** | **Kotlin + Spring Boot 3 + Postgres + Gradle** (see `scale-up/spring_kotlin_jvm.md`) | Java + Spring | Kotlin null-safety + coroutines; Java is fine but loses type-safety wins | gated behind forcing-constraint ADR |

**DB:** Postgres; SQLite for local/single-user; DuckDB for analytics; **justify anything else in an ADR**. **Infra:** one PaaS (Fly, Render, Railway, Vercel); **no k8s until forced** (see `scale-up/when_to_activate.md` for activation criteria). Full template + per-language tooling: `rubrics/stack_decision.md` + `multi-language/matrix.md`.

## Section 3. Defaults (state them; user override OK)

- **Monorepo** if >1 deployable; single repo otherwise.
- **Modular monolith.** Microservices only with **written justification naming the forcing constraint** (Newman: "microservices are a last resort"). See `scale-up/distributed_systems.md` if forcing constraint exists.
- **Trunk-based**, feature-flagged, deploy-on-merge. Release train only if regulated.
- **Semver** for public APIs; **API deprecation policy** (`checklists/deprecation_policy.md`) with `Sunset` and `Deprecation` headers (RFC-8594).
- **ADRs** in `/docs/adr/`. MADR-short for <5 devs, full Nygard for larger.
- **Module boundaries by Parnas:** modules hide *design decisions likely to change*, not flow steps. Enforce architecture decisions with **fitness functions** in CI (`checklists/fitness_functions.md`).
- **Supply chain:** SLSA Build Track L2 minimum (`checklists/supply_chain_slsa.md`).

## Section 4. Refusal list (will not produce without justification)

Refuse to add (default mode): microservices / k8s / service mesh / event bus / CQRS (see `scale-up/` if forcing constraint); a framework off the short list; >3 layers of abstraction at project start (YAGNI); the banned-vocab list (`"enterprise"`, `"scalable"`, `"robust"`, `"leverage"`, etc.): **state the concrete property** (e.g. "p99 < 200ms at 1k RPS"; full list `recovery.skill/templates/deai_rules.md`; base regex `tests/test_self_voice.sh`).

## Section 5. Confidence-score rule (the stop-loss)

**Tier the threshold by reversibility**, three buckets per `rubrics/vibe_safety_map.md` (vibe-safe / vibe-careful / vibe-dangerous); vibe-impossible is handled as a *refusal* classification, not a score threshold.

> ⚠️ **Honest precision warning.** All threshold and per-component-minimum numbers in this section are tagged **`[normative, operator wisdom, uncalibrated]`** until your `.recovery/calibration.jsonl` log reaches **N≥50 scored changes with linked incident outcomes**. Before that, the numbers are *forced precision*: they look exact in a table, but no empirical basis yet justifies "≥95 vs ≥94." **Treat them as procedural defaults, not as calibrated risk thresholds.**
>
> **Below N=10:** the skill renders verdicts as `advisory` only. Do not gate ship/no-ship on the headline number; use the per-component walk-through itself as the value.
>
> **N=10 to N=49:** numeric verdicts permitted but tagged `(uncalibrated, N=<n>)`. The per-component minima are still the load-bearing constraint.
>
> **N≥50:** retier based on observed score-vs-incident correlation. Until you've done that retiering, you are running on operator wisdom, not data.

| Tier | Threshold `(uncalibrated)` | Per-component minima `(uncalibrated)` | Trigger axis |
|---|---|---|---|
| Vibe-dangerous | ≥95 | Test ≥90, Hallucination ≥90, Adversarial ≥85, Reversibility ≥90 | auth, payments, deletes, secrets, schema-breaking, public side-effect |
| Vibe-careful | ≥90 | Test ≥80, Hallucination ≥85, Adversarial ≥70 | public API, dep add, schema-additive, prompt change |
| Vibe-safe | ≥80 | Test ≥70, Hallucination ≥70 | UI tweak, internal helper, log change |

**Pure-refactor sub-row** (rename / extract / format, no behavior change): use vibe-safe with relaxed threshold ≥70 *only if* a behavior-preservation check (golden / characterization / mutation-equivalent) passes; otherwise baseline ≥80.

**Why uncalibrated:** numbers were chosen by operator wisdom for graduated stringency across reversibility tiers. The *ordering* (dangerous > careful > safe) is principled; the *exact thresholds* (95/90/80) are not. Retiering requires score-vs-incident correlation across at least 50 logged entries (`KITCHENHAM-EFFECT-SIZE` methodology, significance ≠ size; demand effect-size + CI). Every scored change must be logged to `.recovery/calibration.jsonl` (schema: `templates/calibration_log_render.md`). Mastery-learning literature (`GUSKEY-2010` `[T1-replicated]`) supports the underlying tier-floor concept; specific values await calibration data.

### Components (each 0–100)

| # | Component | Weight | Full credit |
|---|---|---|---|
| 1 | Code-read depth | 15 | every changed file end-to-end + every direct caller |
| 2 | Test verification | 20 | tests run + assertion density target met + mutation score ≥ tier-target |
| 3 | Hallucination check | 15 | every dep + API + flag + env var verified (registry, author, first-seen ≥30d, current docs) |
| 4 | Bug-class coverage | 12 | CWE Top-25 + applicable OWASP Top 10 (LLM/API/Web) + AI-PR shapes |
| 5 | Adversarial pass | 10 | ≥3 weakest assumptions resolved with falsifiers |
| 6 | Reversibility | 8 | irreversible ops gated; rollback documented + dry-run executed |
| 7 | Doc accuracy | 8 | CLAUDE.md / README / ADRs / fitness functions match new state |
| 8 | Blast radius | 7 | scoped via `tools/blast_radius.py` (algorithm in `docs/blast_radius_algorithm.md`) |
| 9 | Threat model | 5 | STRIDE applied to changed surface (or LINDDUN for privacy-touching changes) |

Sum = 100. Cap headline at 99. **No re-weighting.** Worked examples and anti-gaming rules: `rubrics/confidence_score.md`.

### Iteration protocol

1. Score the plan/change.
2. If score **≥ tier threshold** *and* per-component minima met: ship.
3. If headline below threshold or any minima missed: re-investigate the lowest-scoring component, update plan, re-score. **Budget per iteration**: max 30 minutes wall-clock; if exceeded, escalate to user.
4. **No score-bumping without new evidence.** A re-score that uses the same inputs as the prior score is invalid.
5. After 2 iterations without crossing threshold, escalate with a gap report.

## Section 6. Output format for new-app plans

When user says "plan a new app":
1. Product summary + 3 falsifiable success criteria (e.g. "p99 < 200ms at 1k RPS")
2. Stack recommendation: chosen + rejected + 1-line why each (cite or `[normative]`)
3. Repo tree (<30 lines); single mermaid or text architecture diagram (ports-and-adapters **only if** 2+ adapter implementations planned)
4. Data model (tables + key relationships) + classification (`templates/threat_model.md`)
5. Deployment model (env count, secret handling, CI steps, SLSA target level)
6. First 5 ADRs (MADR-short titles + 1-line context) + CLAUDE.md / AGENTS.md scaffold (ready to commit)
7. 10-question pre-flight checklist (`checklists/preflight_10q.md`)
8. Vibe-safety map naming the vibe-impossible list (`rubrics/vibe_safety_map.md`)
9. Smells to watch in month 3 (3–5 per app shape) (`checklists/smell_catalog.md`)
10. **Fitness functions** ≥3 lint-class CI gates (`checklists/fitness_functions.md`) + **Threat model summary** (STRIDE; LINDDUN if data-flow privacy)

## Section 7. Workflow for adversarial code reviews

Run **3 phases × 4 lenses**, then synthesize.

### Phase 1. Architecture & extensibility
- Module boundaries Parnas-aligned (hide likely-to-change decision, not flow step); Single Responsibility at *module* level
- Extensibility for next 3 plausible features, what breaks?
- Cyclomatic / coupling smells, dead branches, copy-paste tells
- **Fitness-function coverage**: are architecture decisions enforced in CI?

### Phase 2. Bug-class audit (multi-lens). Walk `checklists/INDEX.md` → leaf checklists; each project gets P0/P1/P2 findings.

### Phase 3. Vibe-coding + AI-runtime guardrails
- Review-gate inventory: secrets, deletions, prod, external side-effects
- Test-as-spec: encode the spec or just exercise paths?
- CLAUDE.md / AGENTS.md drift; eval baseline trustworthy (golden dataset 50–100 min, 200–500 prod-ready)
- Supply-chain hygiene: deps pinned with hashes, `pip-audit`/`npm audit`/`govulncheck`, SBOM (CycloneDX or SPDX), SLSA target met
- **Agent-runtime contract**: harness allowlist, ledger, rollback, prompt-injection scan (`agent-runtime/`)

### Synthesis. Compile P0/P1/P2; score per **proposed change**, not per project; iterate to tier-floor before applying.

### GitHub output (trainer-owned)

When findings ship on a pull request, **form-check supplies the ranked findings**; **trainer** formats GitHub per `~/Projects/trainer.skill/references/trainer-github-pr-commentary.md`:

- PR **body:** granular manual test plan (numbered steps, repo paths, launch/reset instructions, expected UI).
- PR **comment:** findings table + **Pedagogy** (≤3 takeaways) + remediate-round meta (`head=`, verdict).
- Re-review after fixes; PATCH the same canonical comment (do not leave stale round-1 verdict).

## Section 8. Posture rules

- **Greenfield = highest vibe budget** (the most vibe-friendly context); brownfield = lower vibe budget. **CLAUDE.md / AGENTS.md scaffold is part of the plan**, not optional. **Test-as-spec:** failing tests for acceptance criteria *first*, then AI implements.
- **Review gates** for: auth, payments, DB migrations, code touching secrets, deletes. Rest can be vibe-shipped if tier per-component minima met (tests pass + types check + lint passes + fitness functions green + supply-chain audit clean).
- **Never use** banned-vocab (`recovery.skill/templates/deai_rules.md`) without the concrete property; **never recommend** microservices / k8s / event bus / CQRS without a forcing-constraint ADR (`templates/forcing_constraint_adr.md`).
- **The skill itself obeys the voice rules.** `tests/test_self_voice.sh` enforces.

## Section 9. Evidence posture

Full citations + tier tags: `references/notes.md` (shipped). Spans Parnas 1972 (module-boundary criteria), Cockburn hexagonal (only if 2+ adapter implementations), SOLID/DDD as heuristics not laws, thin empirical support, forward-pointers only; MITRE CWE Top-25 (2025) for bug-class lens; OWASP Top 10 LLM/API/Web; W3C WCAG 2.2 accessibility; SLSA v1.0; RFC 8594; Ford/Parsons/Kua fitness functions; `SLOP-arXiv` (hallucinated-import vigilance); Shai-Hulud chronology (Wiz/Unit42/CISA/Microsoft) for current supply-chain attack model. Original research dossier archived in a private local-only directory; not shipped, not maintained.

## Section 10. Mini-runbook (the 80% case)

```text
1. Read CLAUDE.md / AGENTS.md + every changed file end-to-end + every direct caller.
2. Write failing test (test-as-spec); diff the smallest plausible change.
3. Verify imports + APIs against real docs (registry, author, first-seen). Run tests; capture before/after; compute mutation score on touched code.
4. Walk applicable checklists (`checklists/INDEX.md`). Score: ≥ tier-floor AND per-component minima → ship behind a flag if vibe-dangerous.
5. Update CLAUDE.md / AGENTS.md / fitness functions if surface area changed; log score to `.recovery/calibration.jsonl`.
```

## Section 11. Anti-scope (what this skill is NOT)

Not a code generator (guides agents that write code; does not write code itself); not a CI scanner runner (defines what to run; host harness runs it); not enterprise-by-default (the `scale-up/` annex requires a forcing-constraint ADR); not a substitute for security review by qualified humans on vibe-dangerous surfaces; not localized (English-only at v2.0).
