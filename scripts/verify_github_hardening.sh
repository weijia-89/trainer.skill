#!/usr/bin/env bash
# verify_github_hardening.sh — layout + apply_branch_protection dry-run smoke.
# sdk-review F1: existence-only verify misses shebang/syntax/python3 regressions.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

test -f SECURITY.md
test -f docs/BRANCH_PROTECTION.md
test -x scripts/apply_branch_protection.sh
grep -q trainer README.md

# sdk-review F1: smoke-test dry-run path (no gh auth or live PUT).
GH_REPO="${GH_REPO:-weijia-89/trainer.skill}" DRY_RUN=1 ./scripts/apply_branch_protection.sh >/dev/null

echo "VERDICT: PASS (github hardening layout + apply script dry-run)"
