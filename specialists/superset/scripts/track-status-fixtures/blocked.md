---
project: fixture-blocked
date: 2026-05-20
operator: fixture
batch_id: 2026-05-20-blocked

agents:
  - name: agentD-blocked-track
    role: code
    phase: 2
    owned_paths:
      - _artifact_blocked_by_dependency.md
    consumes:
      - _artifact_dependency_never_produced.md
    produces:
      - _artifact_blocked_by_dependency.md
    worktree: none-fixture
    wall_clock_min: 30
    status: BLOCKED
---

# Fixture: blocked

Single agent with status=BLOCKED (e.g., waiting on a dependency that did
not land). Expected verdict: `blocked`. The validator does not require
primary evidence to corroborate BLOCKED; the verdict is taken from the
manifest's secondary signal and surfaced for operator attention.
