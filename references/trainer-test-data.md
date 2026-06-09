# Trainer — test data matrix (on-demand)

Load when writing **test plans**, **manual QA**, **demo seeds**, or reviewing PRs that touch fixtures/`loadDemo*`.

## Iron law

**Every claimed test scenario must have reachable data.** If the test plan or manual QA names a state, seeds/fixtures/demo must include at least one row in that state. Uniform seeds (every med has a schedule) block scenarios you cannot reach without ad-hoc DB surgery.

## PR / manual QA gate

1. List scenarios the PR or smoke doc exercises (numbered).
2. Map each to a **data source**: demo seed id, fixture helper, or explicit create steps in the scenario.
3. **BLOCK** (trainer comment) or **REQUEST_CHANGES** when a scenario has no path — e.g. "med without schedule" but demo gives every med a schedule.

### Self-check (add to trainer-github-pr-commentary before POST)

- [ ] Test plan scenarios each name data source (seed id / fixture / create steps).
- [ ] Demo/fixture matrix covers negative and edge states, not only happy path.

## Matrix template (copy minimal rows)

| Scenario | Required state | Data source |
|----------|----------------|-------------|
| … | … | `seed-id` / `loadDemoData` / steps 1–N |

## toebeans minimum matrix (extend per PR)

| Scenario | State | toebeans source |
|----------|-------|-----------------|
| Empty app | no pets | Start fresh (no demo) |
| Demo full path | pet+med+schedule | `loadDemoData` → e.g. `med-luna-methimazole` |
| Med **without** schedule | med, no `Schedule` row | `loadDemoData` → `med-luna-eye-drops` |
| Discontinued med | `discontinued_at` set | unit test `updateMedication`; manual: discontinue in UI |
| Archived pet | `archived_at` set | manual: archive flow when wired |
| Pending dose / alarm | `DoseEvent` pending | demo schedule or `ScheduleCreate` with T+3min |

**Manual QA:** `bash scripts/manual_qa_block.sh` then scenarios from `docs/manual-qa.md`.

## Agent rule

When adding a manual or automated scenario, **update seeds or document create steps in the same PR**. Do not defer matrix gaps to "operator will create manually" unless the scenario is explicitly a create-from-empty flow.
