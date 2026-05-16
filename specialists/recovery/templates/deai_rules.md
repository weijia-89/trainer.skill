---
name: deai_rules
version: 2.0.0
parent_skill: recovery
---

# deAI Rules — voice cleanup with per-archetype overlays

The deAI sweep is one phase in the recovery DAG. It removes vocabulary and shape patterns that mark prose as "AI-generated to a critical reader." Per-archetype overlays prevent the rules from breaking tooling-specific conventions (e.g. Sphinx-required uniform docstrings).

## Base banned vocabulary (applies everywhere except `references/` and `examples/`)

Word-boundary, case-insensitive. Regex (mirrored in `tests/test_banned_vocab.py`):

```
\b(scalable|cutting[- ]edge|enterprise[- ]grade|synergize|synergy|delve|delving|delved|seamless|seamlessly|streamline|streamlining|holistic|paradigm|game[- ]chang(er|ing)|next[- ]gen|state[- ]of[- ]the[- ]art|world[- ]class|best[- ]in[- ]class|empower(s|ed|ing)?|unparalleled|unmatched|navigate(?: the| this| through))\b
```

Quoted/backticked occurrences (e.g. `"scalable"`, `` `leverage` ``) are excluded as **meta-discussion** of the rule. The base test only flags unquoted uses.

If a banned word genuinely fits, **state the concrete property instead**:
- "scalable" → "horizontal scale via stateless workers" or "tested at 10k RPS"
- "delve into" → "examine" / "discuss" / cut entirely
- "seamless" → "transparent" / cut
- "streamline" → name the bottleneck removed
- "world-class" → cut; cite the measured property

## Soft-signal vocabulary (per-archetype overlay only — not flagged in base scan)

These words have legitimate technical uses (`agent harness`, `leverage-per-test`, `robust statistics`, `elevated incidence`). They are caught only by per-archetype overlays where context narrows the meaning:

- **robust / robustly**
- **leverage / leveraging / leveraged** (verb form with object: "leverage X to Y")
- **harness / harnessing / harnessed** (verb form: "harness the power of"; not the noun "agent harness")
- **elevate / elevates / elevated** (verb form: "elevate productivity"; not "elevated incidence")

When an archetype overlay is active (e.g. README, marketing copy review), these become hard flags. In source code, runbooks, and architectural docs, they are permitted.

## Sentence-shape signals (deprioritize in favor of base + structure rules)

These are softer signals; flag for review, do not block:

- Opening with "In conclusion," / "Furthermore," / "Moreover," / "It is worth noting that,"
- Tricolons more than once per page ("planning, executing, and reviewing"; "fast, reliable, and secure")
- Em-dashes — used three or more — times in one paragraph
- Sentence variance below ~10 (run-on uniformity); too-short below 6
- Hedge stacks ("could potentially", "might possibly", "may perhaps")

## Per-archetype overlays

### `api-reference` overlay (Sphinx / typedoc / Javadoc / godoc / rustdoc)

API reference docstrings are extracted by tooling. Drop conversational hedges; allow uniform shape; permit terms that base would flag:

- Allow: "deprecated", "see also", "internal", "experimental"
- Allow: imperative voice ("Returns the foo.", "Raises ValueError when x < 0.")
- **Require uniform docstring shape** (one-line summary, blank line, longer description, parameters, returns, raises, examples)

### `runbook` overlay

Imperative voice; role-segregated; no first-person.

- Drop: "we should", "we'll", "let's", "in our experience"
- Allow: imperative directives ("Run X.", "If output Y, do Z.")

### `readme` overlay

Most relaxed; conversational tone allowed; archetype-driven (CLI / library / service / monorepo per `form-check.skill/templates/README_archetypes/*`).

- Allow: contractions, second person ("you")
- Discourage: marketing copy, "vision" sections, autobiography
- Still ban: base banned vocabulary

### `architecture` overlay

Descriptive third-person.

- Drop: first-person ("I think", "we decided")
- Drop: editorial hedges ("perhaps", "arguably") in normative sections
- Allow: explicit `[normative]` / `[verified]` tags
- Cite ADRs by number when referencing decisions

### `changelog` overlay

Impersonal factual (Keep-a-Changelog).

- Drop: first-person, second-person
- Drop: subjective adjectives ("major improvement", "huge fix")
- State the change in past tense (Added / Changed / Fixed / Removed / Deprecated / Security)

### `roadmap` overlay

Dated, blunt. Won't-do entries load-bearing.

- Drop: aspirational copy ("we hope to", "ideally")
- Allow: dated commitments
- Require: explicit "Won't-do" section with reasons

### `glossary` overlay

Precise definitions; no examples.

- Drop: examples in entries (examples belong in cookbook / user docs)
- Drop: hedging in definitions

### `source-comments` (non-API-reference) overlay

Mixed density preserves the intent of base rules without breaking docstring tooling.

- Don't comment every line; do comment the non-obvious ones
- Code that explains itself doesn't need comments
- Comments that describe *why* (not *what*) are most useful

## How the overlay is selected

The recovery deAI-sweep phase applies overlays based on file path:

```
README.md                       → readme overlay
CHANGELOG.md                    → changelog overlay
ARCHITECTURE.md                 → architecture overlay
ROADMAP.md                      → roadmap overlay
SECURITY.md                     → architecture overlay (descriptive parts) + runbook overlay (imperative parts)
docs/glossary.md                → glossary overlay
docs/runbooks/*.md              → runbook overlay
docs/adr/*.md                   → architecture overlay
docs/api/*.md                   → api-reference overlay
src/**/*.{py,ts,...} docstrings → api-reference overlay (extracted by tooling)
src/**/*.{py,ts,...} comments   → source-comments overlay
```

Files not matching any pattern get base only.

## Enforcement

- `tests/test_deai_regex.py` runs base + selected overlay against fixtures.
- `tests/test_self_voice.sh` runs base regex over the skill's own content (excluding `references/` and `examples/`). The skill must obey its own voice rules.
- A repo's CI fitness function runs deAI sweep against repo prose; PR cannot merge without 0 base hits.

## Anti-patterns

- Applying base rules to API reference docstrings → breaks Sphinx / typedoc generation.
- Banning every flagged word reflexively → over-correction; cut concrete value.
- Substituting one banned word for a synonym ("robust" → "powerful") → defeats the rule.
- "Voice cleanup" used as a euphemism for content rewrite — separate concerns.
