# program.skill ROADMAP

**Current version:** v0.3.0 (synced with trainer v0.5.0)
**Status:** stable. The one-page spec template, the kill-criteria
prompt, and the "name the first user" forcing function all ship in
working form.

## Near-term

- Pressure-scenarios for the vague-project failure modes: scope creep
  inside the first session, a one-pager that has acceptance criteria but
  no kill criteria, "I want to build X" without a named user, the
  spec-quality death spiral where the doc grows but the project doesn't.
- A worked example of a real project that went from vague idea to
  shippable one-pager, with the version history of the spec visible.

## Mid-term

- A "spec is failing" checklist for in-flight projects. Currently program
  handles the cold start well; the warm-but-stuck case is under-served.
- Better handoff to form-check once the spec has acceptance criteria
  and a first PR is in flight.

## Out of scope

- Project management method. program is a one-pager surface, not a PM
  framework.
- Estimation. The skill teaches "name the first user;" it doesn't try to
  predict how long anything takes.

## Open questions

- Whether to enforce a hard word limit on the one-pager. Currently 1-2
  pages is the soft norm; a hard cap might force harder cuts.
