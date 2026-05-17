# recovery.skill ROADMAP

**Current version:** v0.4.0 (synced with trainer v0.5.0)
**Status:** stable. The full-engagement scorecard, the launch-readiness
checklist, and the code-fixer confidence rubric all ship in working form.

## Near-term

- Add Phase 11 pressure-scenarios for the recovery flow. First wave:
  incident triage plus post-mortem authoring. Second wave:
  hardening-before-launch sweeps and the refusal cases where the right
  call is "do less, not more."
- Document the handshake with `pr.skill` and `diet.skill` so a project
  that lands in recovery has a clean exit ramp into routine deploy and
  steady-state observability.

## Mid-term

- Worked examples of bad calls the recovery flow caught (or missed) in
  real engagements. Currently the skill ships with rubrics but no
  concrete after-action reports.
- A "recovery is the wrong skill" decision-tree entry: route to program
  (still vague) or form-check (single PR review) when the engagement
  doesn't actually call for a multi-day rebuild.

## Out of scope

- Automated incident detection. recovery operates after a human or a
  monitor has already raised an alarm.
- Recovery for non-software projects.

## Open questions

- Whether the launch-readiness checklist should be a hard gate or stay
  advisory. Current stance is advisory; the engagement owner makes the
  call.
