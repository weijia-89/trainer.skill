# Fixtures for validate-track-status.sh

Each fixture is a minimal daily-log file that exercises one VERDICT class
emitted by `scripts/validate-track-status.sh`. The fixtures are designed
to work in the no-git project context (superset.skill itself is no-git),
so they do not depend on real git branches; the validator's branch check
degrades to N/A.

## Fixtures

| File | Expected VERDICT | What it exercises |
|---|---|---|
| `valid-dispatch.md` | `valid-dispatch` | status=DONE with all `produces` paths present on disk |
| `undispatched.md` | `undispatched` | status=PLANNED with no branch and no produces evidence |
| `status-unverified.md` | `status-unverified` | status=DONE but `produces` path absent from disk |
| `blocked.md` | `blocked` | status=BLOCKED |

## Project-root resolution

Fixtures pass `--project-root .` (current directory) via the test runner
so that the relative `produces:` paths inside each fixture resolve under
this fixtures directory.

The `valid-dispatch.md` fixture's produces path is
`track-status-fixtures/_artifact_valid_dispatch.md` (the marker file in
this directory), which exists on disk. The `status-unverified.md` and
`undispatched.md` fixtures reference paths that intentionally do not
exist.

## Run

From the superset.skill root:

```
bash scripts/validate-track-status.sh \
  scripts/track-status-fixtures/valid-dispatch.md \
  scripts/track-status-fixtures
```

Verify the final line contains `VERDICT: valid-dispatch`.
