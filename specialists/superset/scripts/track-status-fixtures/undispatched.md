---
project: fixture-undispatched
date: 2026-05-20
operator: fixture
batch_id: 2026-05-20-undispatched

agents:
  - name: agentB-undispatched-track
    role: code
    phase: 1
    owned_paths:
      - _artifact_never_created.md
    consumes: []
    produces:
      - _artifact_never_created.md
    worktree: none-fixture
    wall_clock_min: 30
    status: PLANNED
---

# Fixture: undispatched

Single agent with status=PLANNED and produces path that does not exist.
The branch lookup returns no match (the agent name is unique to this
fixture). Expected verdict: `undispatched`.
