# pr.skill ROADMAP

**Current version:** v0.3.0 (synced with trainer v0.5.0)
**Status:** stable. The deploy decision tree, the rollback path, and
the "your deploy isn't done until verification passes" pattern all ship
in working form.

## Near-term

- Pressure-scenarios for the common deploy failure modes: secrets that
  weren't in the deploy env, missing rollback path discovered post-fail,
  post-deploy verification that runs but doesn't actually verify, and
  the "we're rolling forward because rollback feels worse" trap.
- A worked example of a real first deploy of a new service, with the
  artifacts (env var inventory, rollback runbook, verification script)
  shown end to end.

## Mid-term

- Coverage for canary and blue-green patterns beyond the generic
  shape. Today the skill assumes a single-rollout model and degrades
  gracefully but doesn't help much with canaries specifically.
- A "deploy adjacency" map: when to route into diet (operate), recovery
  (something broke), safetybar (you just did something scary).

## Out of scope

- pr is not a CI/CD provider tutorial. It's the human decision surface
  around the deploy step.
- Infrastructure-as-code style guides. Adjacent but tool-specific.

## Open questions

- Whether the post-deploy verification template should be code or prose.
  Prose covers more cases; code is testable.
