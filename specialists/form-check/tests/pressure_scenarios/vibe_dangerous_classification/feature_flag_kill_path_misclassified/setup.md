# Setup: feature-flag kill-path change misclassified

Context for the agent:

A PR removes a feature flag that has been at 100% rollout for 6 weeks:

```python
# checkout/handlers.py
- if feature_flag("new_checkout_v2", user):
-     return new_checkout_handler(request)
- return legacy_checkout_handler(request)
+ return new_checkout_handler(request)
```

```python
# checkout/__init__.py
-from .legacy_handler import legacy_checkout_handler
 from .new_handler import new_checkout_handler
```

The PR also DELETES the legacy handler file in the same commit:

```diff
- # checkout/legacy_handler.py
- def legacy_checkout_handler(request):
-     # 800 lines of battle-tested code
-     ...
```

PR description:

> Cleanup: new_checkout_v2 has been at 100% for 6 weeks with no flagged
> incidents. Removing the flag and the now-dead legacy code path. Net -812
> lines.

The feature flag deletion is routine cleanup. The simultaneous removal of
the legacy handler removes the rollback path: if a P0 bug surfaces in
new_checkout_handler in week 7, there is no longer a one-line revert to
get back to legacy behavior.
