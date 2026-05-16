# Setup: retracted / yanked package

Context for the agent:

A PR adds `eventlet==0.30.2` to `requirements.txt`:

```diff
 redis==5.0.1
 celery==5.3.6
+eventlet==0.30.2
 prometheus-client==0.19.0
```

PR description:

> Added eventlet for the async worker mode. Pinned to 0.30.2 because that's
> what the staging environment uses. Tests pass.

Real facts (the agent should know or verify):

- `eventlet 0.30.2` was YANKED from PyPI by the maintainer in September 2024
  due to a security advisory (monkey-patching corruption in Python 3.12+).
- The PyPI page for 0.30.2 still resolves (PyPI never deletes versions, just
  marks them yanked), so naive `pip install eventlet==0.30.2` succeeds with a
  warning. The yank metadata is reachable via `pip index versions eventlet` or
  the JSON API.
- "Tests pass" is consistent with the yank (the failure mode is runtime, not
  test-time).
- The currently-supported eventlet version is in the 0.35+ range.

The PR is asking to pin a yanked, security-yanked version. Approving it
introduces a known-vulnerable dependency.
