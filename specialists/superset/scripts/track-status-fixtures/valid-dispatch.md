---
project: fixture-valid-dispatch
date: 2026-05-20
operator: fixture
batch_id: 2026-05-20-valid-dispatch

agents:
  - name: agentA-valid-dispatch
    role: code
    phase: 1
    owned_paths:
      - _artifact_valid_dispatch.md
    consumes: []
    produces:
      - _artifact_valid_dispatch.md
    worktree: none-fixture
    wall_clock_min: 30
    status: DONE
---

# Fixture: valid-dispatch

Single agent with status=DONE and produces path present on disk.
Expected verdict: `valid-dispatch`.
