# gymbuddy.skill ROADMAP

**Current version:** v0.3.1 (synced with trainer v0.5.0)
**Status:** stable. The over-reliance signal list and the "did you read
the diff" prompt are the core surface and don't need to grow.

## Near-term

- Pressure-scenarios for the two most common over-reliance failure
  modes: diff-accepted-unread, and AI-explanation-confident-but-wrong.
  The "perceived speed greater than measured speed" failure is harder to
  test in a scenario and comes later.
- A short worked example: a real session where gymbuddy caught a
  hallucinated import before it landed in the diff.

## Mid-term

- Calibration data on which signals fire most often in real sessions.
  Currently the signal list is from training intuition; a few months
  of `.recovery/calibration.jsonl` data would let us prune.

## Out of scope

- gymbuddy is not a code reviewer. That's form-check. Resist the urge to
  grow gymbuddy into one.
- Tool detection of AI-generated code in the wild. Adjacent skills
  (deai, vibe-check) cover that surface. The failure modes for
  detection are different from the failure modes for over-reliance.

## Open questions

- When should gymbuddy hand off to form-check? Today the heuristic is
  "you have a diff in hand;" tighter rules would help.
