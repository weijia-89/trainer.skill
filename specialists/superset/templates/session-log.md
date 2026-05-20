# Session log template

The dispatched agent writes this to `<project>/localonly/session-logs/<DATE>-agent<N>-<task-slug>.md` after commit, before returning.

Target: 300-600 words. Project voice rules apply (no em-dashes, no theatrical fragments, active voice).

---

```markdown
# Session log: Agent <N>, <task-slug>, <DATE>

## Task summary (~50 words)
What was asked; what shipped.

## Outcome
- Commits: <SHAs>
- Tests: <N> passed, 0 new failures
- Wall-clock: ~<minutes> from baseline capture to commit
- Result: success / partial / blocked

## Decisions made (~150 words)
Non-obvious choices, one bullet each:
- **<decision>:** <chosen option>. Rationale: <one sentence>. Alternatives considered: <list>.

## Surprises (~100 words)
Anything that diverged from the prompt's assumptions. File counts off, instructions ambiguous, tool returned unexpected output. For each: what happened, how I handled it, whether the prompt should have anticipated it.

## Errors encountered (~50 words)
List failures (test breaks, tool errors, syntax issues). For each: error, recovery action, time cost.

## Tool + skill usage notes (~50 words)
- Skills loaded: <list>
- Useful: <subset>
- Noise: <subset, if any>
- Inefficient tool sequences (if any): <description>

## Prompt-improvement signal (~100 words)
Specific, actionable changes I would make to the prompt next time. Examples:
- "The semantic-check section was overweight for the actual em-dash variety encountered."
- "Cwd-parameter callout could be a one-line cap at top rather than embedded in First Steps."
- "Baseline-capture step should use `pytest --collect-only -q` to count tests without running them; faster."

## Patterns to extract (~50 words, optional)
Recurrences that might become a skill or rule. Examples:
- "Em-dash sweep + voice-rule audit across N file types is a candidate skill."
- "Vibe-safe declaration after trainer-load saves coaching tokens for mechanical work."
- "Capture-baseline-then-compare-after pattern generalizes to any sweep task."

## Files touched
Bullet list: `<path>` (one-line description).
```

## Notes for the agent writing the log

- If a section has nothing to report, write `None`. Brevity is the point.
- Voice rules apply to your prose: no em-dashes (U+2014), no "X, not Y" colon-framings, no theatrical paragraph-ending fragments, no tricolon-after-colon, active voice with "I".
- The log is for pattern extraction by the operator (or a future `harness-review` agent). Optimize for searchability and pattern density, not narrative.
- Write the log BEFORE returning the operational summary. If you crash or get interrupted, the partial log is still useful debug.
