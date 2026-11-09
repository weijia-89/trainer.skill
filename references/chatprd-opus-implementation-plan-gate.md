# ChatPRD Opus 4.6 implementation plan gate (significant work)

**When:** the build is significant before any code exists. The router fires on
refactors, rewrites, patches over five files, or canon-to-template work. Small
fixes and doc edits do not need this gate.

**Why:** multi-file changes fail from plan defects, not from bad code. ChatPRD
plans are written and shaped outside the coding session, so the plan gets an
independent pass before any file is touched. The operator controls the merge
point.

## The flow

1. **Plan first.** The agent writes an implementation plan: goal, exact file
   list, phase order, and verification per phase. No source edits yet.
2. **Export to ChatPRD.** Send the plan to ChatPRD Opus 4.6 with the mash repos
   attached. Mash repos are the ground truth the plan must match; attach them
   in ChatPRD, not as pasted text.
3. **Handoff packet.** ChatPRD works from a prompt the agent prepared. Keep the
   packet inside the tool's length limit.
4. **Operator saves the ingest file.** Cursor implements only after the
   operator saves `implementation_plan_*_ingest.md` in the repo tree. The file
   name prefix is the contract: no ingest file, no implementation.
5. **Implement from the ingest file.** The executing session reads the ingest
   file and follows it. Deviations go back through a plan update, not a silent
   edit.

## Waiver

`waive-chatprd-plan` is a coached override for cases where the gate cost
exceeds its value (single-session hotfix, throwaway prototype). The waiver is
stated before code moves and recorded in the session log. It is not a default.

## Forbidden

- Implementing a gated change without `implementation_plan_*_ingest.md` on disk.
- Treating a ChatPRD chat reply as approval. Only the saved ingest file counts.
- Pasting repos into ChatPRD instead of attaching the mash.
- Skipping phase verification inside the plan because the plan came from
  ChatPRD. The plan gate and the per-phase gates stack, never replace.
