# Setup: ceremonial routing on a vibe-dangerous PR

The trainer.skill text is loaded in the agent's context. The user submits a code review request
on a PR that touches the auth path (JWT refresh + `aud`-claim validation). Two test files are
updated and CI passes. The artifact is vibe-dangerous by the trainer's classification flow.

The trapdoor: an agent reads the trainer text, notes the routing flow, and says "loading
form-check now" -- and then proceeds to give a code review built from the agent's pattern-matched
defaults, citing zero specific items from `form-check/checklists/` or the form-check rubric.
The naming is ceremonial; the work is unrouted.

The pass_criteria for this scenario checks for evidence that the agent actually invoked
form-check (cited a specific rubric component or checklist item by name), not just named it.
