#!/usr/bin/env bash
# verify_trainer_codereview.sh — anti-theater code review contract self-test.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT/tests/trainer_codereview/test_trainer_codereview_contract.py" -v
bash "$ROOT/scripts/test_ci_trainer_pr_review_gate.sh"
echo "# verify_trainer_codereview: PASS"
