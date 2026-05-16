---
name: python_tooling
version: 2.0.0
parent_skill: form-check
---

# Python — tooling depth

## Tooling matrix (Python row of `matrix.md`)

| Concern | Tool | Notes |
|---|---|---|
| Test runner | pytest | with `pytest-asyncio`, `pytest-json-report` |
| Property-based | Hypothesis | profiles: dev (~50 examples), CI (~500) |
| Mutation | mutmut OR cosmic-ray | mutmut for speed; cosmic-ray for richer mutations |
| Linter + formatter | ruff | replaces flake8 + isort + black + many plugins |
| Type checker | mypy or pyright | mypy: deeper; pyright: faster, better IDE |
| Dep audit | pip-audit | fail CI on any high; Socket.dev for slopsquatting depth |
| Lockfile | `uv lock --generate-hashes` | also `pip-tools` if uv unavailable |
| Fuzzing | Atheris (Google) | OSS-Fuzz integration via Atheris |
| Secrets scan | detect-secrets, trufflehog | pre-commit hook |
| IaC lint | checkov, tfsec | for Terraform / CloudFormation / Helm |
| SBOM | cyclonedx-py | per release |

## Test-as-spec example

```python
# tests/unit/test_html_truncation.py
import pytest
from hypothesis import given, strategies as st

from src.auditor import _truncate_html

@given(html=st.text(min_size=0, max_size=10_000))
def test_truncation_is_idempotent(html):
    once = _truncate_html(html, 3000)
    twice = _truncate_html(once, 3000)
    assert once == twice
    assert len(once) <= 3000

@given(html=st.text(min_size=0, max_size=10_000))
def test_truncation_does_not_split_html_tag(html):
    truncated = _truncate_html(html, 3000)
    # invariant: truncated content does not end mid-tag
    if "<" in truncated:
        last_open = truncated.rfind("<")
        last_close = truncated.rfind(">")
        assert last_close > last_open or last_open == -1, \
            f"truncation split a tag: {truncated[-50:]!r}"
```

`tests/conftest.py`:

```python
import os
from hypothesis import settings, HealthCheck

settings.register_profile("ci", max_examples=500, deadline=None,
                          suppress_health_check=[HealthCheck.too_slow])
settings.register_profile("dev", max_examples=50)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
```

## Fitness function example (lint-class)

Project-local script (place at *tools/check_module_boundaries.py* in the consumer repo):

```python
"""Forbid imports from internal modules outside their package.

ADR: docs/adr/0007-module-boundaries.md.
"""
from __future__ import annotations
import ast
import sys
from pathlib import Path

ALLOW = {
    "core": {"core", "shared"},
    "api": {"api", "core", "shared"},
    "internal": {"internal"},  # internal is closed
}

def check(file_path: Path) -> list[str]:
    """Return list of violation strings for a single file."""
    pkg = file_path.parts[1]  # src/<pkg>/...
    if pkg not in ALLOW:
        return []
    tree = ast.parse(file_path.read_text())
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top not in ALLOW[pkg] and top in ALLOW:
                violations.append(
                    f"{file_path}:{node.lineno} imports from '{top}' "
                    f"but is in package '{pkg}' (allow={sorted(ALLOW[pkg])})"
                )
    return violations

if __name__ == "__main__":
    all_violations: list[str] = []
    for f in Path("src").rglob("*.py"):
        all_violations.extend(check(f))
    if all_violations:
        for v in all_violations:
            print(v)
        sys.exit(1)
```

Wire into pre-commit + CI.

## Common pitfalls

- **`requirements.txt` without hashes**: defeats the lockfile. Use `uv lock` or `pip-compile --generate-hashes`.
- **`requests` without timeout**: hangs forever on slow servers. Always pass `timeout=`.
- **`subprocess.run(..., shell=True)` with f-string**: CWE-78 territory. Use `args=[...]` form.
- **`yaml.load` instead of `yaml.safe_load`**: arbitrary code execution. Always `safe_load`.
- **`pickle.load` from untrusted source**: arbitrary code execution. Use JSON / msgpack / Pydantic instead.
- **`eval` / `exec` over user input**: never.
- **Mutable default arguments**: `def f(x=[]):` shares the list across calls.
- **Eager imports inside `__init__.py`** of large packages: slow startup; circular import risk.
- **`asyncio.get_event_loop()` in 3.12+**: deprecated; use `asyncio.run()` or `asyncio.get_running_loop()`.
- **Bare `except:`**: swallows `KeyboardInterrupt` and `SystemExit`. Use `except Exception:` minimum.

## Concurrency

Default to **Trio + AnyIO** for new code. Trio's structured concurrency (nurseries, level-triggered cancellation) is safer than asyncio's edge-triggered model. AnyIO bridges trio↔asyncio so library code can run on either runtime.

If asyncio is mandated:
- Always create tasks via `TaskGroup` (3.11+), not `asyncio.create_task` (lifecycle is harder to track).
- Use `asyncio.timeout` (3.11+) for cancellation.
- Avoid sharing mutable state across tasks; use queues.

## Pydantic v2

- All boundary contracts as Pydantic models.
- `model_validate_json` for input; `model_dump_json` for output.
- Use `Annotated[…, Field(…)]` not class-level field magic.
- For performance-critical paths, profile before optimizing.
