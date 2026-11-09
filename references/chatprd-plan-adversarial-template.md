# ChatPRD plan adversarial review (mash-grounded template)

**When:** a ChatPRD draft plan exists and the operator is about to save the
ingest file. Run this review against the attached mash repos before approval.
The review is the last defect filter at the cheapest point to fix: the plan.

**Rule:** every claim in the plan is grounded against the mash, not against the
plan's own text. A plan that cites a function that does not exist in the mash
fails here, before it becomes code.

## Template

Copy per plan and fill every section. A section with no findings still gets a
written "none" line: silence is not evidence.

```
## Claims inventory
List every load-bearing claim: file paths, symbols, interfaces, ordering.
One row each, with where the plan states it.

## Grounding check
For each claim above: matched against the mash? source file + line?
- CONFIRMED  <file:line>
- MISMATCH   <file:line + what the mash actually shows>
- UNGROUNDED <claim the mash cannot confirm>

## Boundary cases
First input, last input, empty input, duplicate input, concurrent input.
Does the plan's design name the behavior for each? Missing rows FAIL.

## Failure and rollback story
What happens when each phase fails mid-flight? Can the operator recover
without hand-editing? If the plan has no answer, BLOCK.

## Verification per phase
Which command proves each phase done? "Tests pass" is not an answer;
name the suite or script.

## Verdict
APPROVE / BLOCK per section, then overall. BLOCK items get one line of
fix guidance, not a rewrite.
```

## Posture

Read the plan as an adversary, not as a collaborator. The default question is
"what does this plan quietly assume", and the mash answers it. The review
budget is bounded: one full pass, one fix round, then the operator decides
with the findings on the table.
