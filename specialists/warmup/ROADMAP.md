# warmup.skill ROADMAP

**Current version:** v0.3.0 (synced with trainer v0.5.0)
**Status:** stable. Front-desk routing across the gym family is the core
surface; the question-routing decision tree and the "I don't know yet"
escape hatch both ship in working form.

## Near-term

- Pressure-scenarios for the routing failure modes: requests that span
  multiple specialists, requests where the user has the wrong mental
  model of what's available, the "I'll just ask trainer directly" bypass
  pattern, and ambiguous safety classifications that should fail safe.
- A worked example of a learner's first three sessions across the gym,
  showing the route decisions and the handoffs.

## Mid-term

- Coverage data on which routing decisions warmup gets wrong most often.
  This needs `.recovery/calibration.jsonl` events tagged with the
  proposed route and the eventual route.
- Better routing into program when a request is "let's build X" but the
  spec doesn't exist yet. Currently warmup tends to route into form-check
  or pr too early.

## Out of scope

- Routing decisions for skills outside the gym family. That's trainer's
  job.
- Auto-routing. warmup proposes; the user disposes.

## Open questions

- Whether warmup should have a session-memory of past routing choices,
  or stay stateless. Stateless is simpler; session memory might catch
  the "you always end up in form-check" pattern earlier.
