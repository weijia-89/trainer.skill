# diet.skill ROADMAP

**Current version:** v0.3.0 (synced with trainer v0.5.0)
**Status:** stable. Steady-state observability surface and the post-deploy
sweep pattern ship in working form. The runbook templates are the active
growth area.

## Near-term

- Pressure-scenarios for the common operational confusions: alarm fired
  but no one understands what it means; deploy made things worse but the
  rollback path isn't obvious; post-mortem deadline pressure pushing
  toward "we'll fix it next sprint."
- A worked example of a real post-deploy investigation, end to end, so
  the skill has a concrete reference instead of only abstract rubrics.

## Mid-term

- Coverage for monitoring stacks beyond the current generic shape:
  Datadog, Honeycomb, CloudWatch, OpenTelemetry. The skill should name
  the tool when relevant, not pretend they're interchangeable.
- A "diet didn't catch this" failure log so the skill's blind spots are
  visible to future users.

## Out of scope

- diet is not an incident commander. It's the steady-state surface
  before an incident, and the post-mortem surface after. Active
  incident response goes through recovery.
- SLO and SLA arithmetic. It's adjacent material that depends heavily on
  which tool you use, and the friction lives below the skill layer.

## Open questions

- Whether to ship a sample alert-noise audit checklist or keep that
  prose-only. Risk: a checklist creates a false floor.
