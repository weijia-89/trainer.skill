#!/usr/bin/env bash
# verify_github_hardening.sh — layout + apply_branch_protection dry-run smoke.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

test -f SECURITY.md
test -f docs/BRANCH_PROTECTION.md
test -x scripts/apply_branch_protection.sh
grep -q trainer README.md

# Smoke-test canonical dry-run path (no gh auth or live PUT).
GH_REPO="${GH_REPO:-weijia-89/trainer.skill}" DRY_RUN=1 ./scripts/apply_branch_protection.sh >/dev/null

# sdk-review F2: non-canonical truthy DRY_RUN (e.g. 01) must stay dry-run, not live-PUT.
dry_run_out="$(GH_REPO="${GH_REPO:-weijia-89/trainer.skill}" DRY_RUN=01 ./scripts/apply_branch_protection.sh 2>&1)"
echo "$dry_run_out" | grep -q 'DRY_RUN=1 — would PUT'

echo "VERDICT: PASS (github hardening layout + apply script dry-run)"
