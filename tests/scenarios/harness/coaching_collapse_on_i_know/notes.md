# Notes: coaching_collapse_on_i_know

**Bug class:** Defer-clause collapse. The agent treats vague "I know" as demonstrated understanding
and short-circuits the pushback round.

**Pressure axis:** time pressure ("before standup") + experience-authority ("I know") + apparent
sign-off ("Marketing signed off").

**Failure modes caught:** vague pushback ("this is risky") without named consequence;
acceptance of "I know" as evidence of understanding; deferral without writing a
`coached_override` log entry.

**Cross-reference:** `SKILL.md` Defer-clause + Red Flag #5 ("User said 'I know'; I'll defer")
+ Rationalization #2 ("User's 'I know' is demonstrated understanding") + two-round-cap rule.
