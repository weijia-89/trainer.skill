---
project: fixture-status-unverified
date: 2026-05-20
operator: fixture
batch_id: 2026-05-20-status-unverified

agents:
  - name: agentC-status-unverified-track
    role: code
    phase: 1
    owned_paths:
      - _artifact_claimed_but_missing.md
    consumes: []
    produces:
      - _artifact_claimed_but_missing.md
    worktree: none-fixture
    wall_clock_min: 30
    status: DONE
---

# Fixture: status-unverified

Single agent with status=DONE but produces path absent from disk.
Catches the iron-law's target failure mode: the manifest (SECONDARY)
claims completion, but PRIMARY evidence (file on disk) contradicts.
Expected verdict: `status-unverified`.
