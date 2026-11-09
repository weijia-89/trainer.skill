# Phase implementation gate (multi-phase slices)

**When:** work is too big for one slice: multi-phase builds, MASTER-contract
slices, or anything the orchestrator planned as more than one phase. The gate
governs movement between phases, not the work inside a phase.

**Why:** the classic multi-phase failure is a phase that was never verified
becoming the base of the next one. The gate makes verification a movement
permit: no proof, no next phase.

## The gate, phase by phase

Each phase carries four items before any next phase starts:

1. **Plan.** The phase restated in five bullets or fewer, with the exact file
   list. A phase with no file list is not planned yet.
2. **Context.** All planned files read before building; scratchpad or session
   log holds the captured plan, findings, and open questions.
3. **Verification.** A named command with real output proving the phase did
   what its bullets said. "Should pass" is not an output.
4. **Gate check.** An explicit go from the operator (or the orchestrator's
   own approval gate) before the next phase starts. Internal rework loops do
   not need the gate; phase crossings do.

## Slices, retries, and escalation

- A phase that fails verification twice goes to the operator with the full
  failure record, not to a third silent attempt.
- Phases are ordered so that a halted run leaves a coherent tree: never plan a
  phase that depends on unverified work from two phases back.
- A phase outcome lands in the log (logbook or scratchpad) before the phase
  closes: what was verified, by which command, at which commit.

## Forbidden

- Starting phase N+1 while phase N has no verification evidence.
- Collapsing two planned phases into one unlisted mega-pass.
- Marking a phase done by plan intent instead of command output.
- Skipping the gate because the phase looked fine. The eye is a claim;
  the command output is the evidence.
