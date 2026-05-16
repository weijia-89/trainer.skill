# diet — the daily discipline that supports the lifts

A skill for keeping shipped software running and for responding to incidents without making things worse.

## What it does

Once your code is in production, two failure modes start mattering: you stop knowing whether it works, and when it breaks you panic. `diet` covers both.

Steady-state mode:

- Minimum-viable instrumentation (logs, error tracking, four golden signals, uptime check)
- A daily/weekly/monthly operating cadence
- A calibration discipline applied to production behavior

Incident mode:

- A 30-minute incident protocol with explicit forbidden moves
- A four-question incident triage
- The rollback decision rule
- A blameless post-mortem template

The forbidden moves are the load-bearing part. Most beginner production disasters come from panicked destructive actions during an incident. The §3 protocol exists to slow you down for long enough to avoid them.

## When to invoke

- **Steady-state setup**: you just deployed and do not know what to instrument.
- **Steady-state check**: a daily or weekly look at whether your app is behaving normally.
- **Incident**: something is broken right now. Go directly to §3. Do not read §1 first.

## When to skip

- You have a dedicated ops team. This skill is calibrated for solo and small-team contexts.
- You are pre-deploy. Use `recovery` or `pr` instead.

## Composes with

- `form-check` — incident triage uses the threat-model and reversibility rubric components.
- `pr` — rollback paths are documented in `pr §5`; this skill links there.
- `safetybar` — when a code-level rollback is required, this skill hands off there.

## What this skill protects against

The Replit/Lemkin July 2025 pattern: ship → break → panicked destructive action → make it worse. The §3 forbidden-moves list (no destructive commands, no force-push, no in-incident migrations, no deletes, no instrumentation disables) is named for exactly that failure mode. If any of those moves looks like the obvious fix during an incident, write it down and consult a second human before executing.

## Files

- `SKILL.md` — the five sections (instrumentation, cadence, incident protocol, post-mortem template, escalation)
- `CHANGELOG.md` — version history
- This file

## License

MIT.
