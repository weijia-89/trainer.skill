#!/usr/bin/env bash
# Self-test for ci-trainer-pr-review-gate.sh (fixture mode, no gh).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GATE="$ROOT/scripts/ci-trainer-pr-review-gate.sh"
FIXTURE_DIR=$(mktemp -d)
trap 'rm -rf "$FIXTURE_DIR"' EXIT

pass() { echo "PASS  $1"; }
fail() { echo "FAIL  $1"; exit 1; }
expect_pass() {
  local label=$1
  shift
  if "$@"; then
    pass "$label"
  else
    fail "$label"
  fi
}
expect_fail() {
  local label=$1
  shift
  if "$@"; then
    fail "$label"
  else
    pass "$label"
  fi
}

good="$FIXTURE_DIR/good.json"
cat >"$good" <<'JSON'
[
  {
    "body": "<!-- trainer-codereview-toebeans-feat-style-lab-compose-alignment -->\n<!-- head=805402b verdict=APPROVE round=1 -->\n\n### Bug inventory\n\nNo P0–P4 findings — fixture self-test with verify harness.\n\n### Automated verification\n\n- [x] `bash scripts/verify_toebeans.sh` — exit 0\n\n### Trainer notes\n\n1. **Program notes:** test\n2. **Your form:** test\n3. **Next session:** test\n"
  }
]
JSON

expect_pass "valid marker + head + trainer notes + bug inventory" \
  env TRAINER_PR_REVIEW_FIXTURE="$good" \
  TRAINER_PR_BODY_FILE="$ROOT/tests/trainer_codereview/fixtures/pr_body_good.md" \
  bash "$GATE" 99 805402b886b160d3acaf9130cba1363edb1a4d7e feat/style-lab-compose-alignment weijia-89/toebeans

bad_inv="$FIXTURE_DIR/bad-inventory.json"
printf '%s\n' '[{"body": "<!-- trainer-codereview-toebeans-feat-x -->\n<!-- head=abcdef0 verdict=APPROVE -->\n### Trainer notes\n1. **Program notes:** x\n2. **Your form:** x\n3. **Next session:** x\n"}]' >"$bad_inv"
expect_fail "missing Bug inventory rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$bad_inv" \
  bash "$GATE" 1 abcdef0123456789abcdef0123456789abcdef0 feat/x weijia-89/toebeans

bad_ped="$FIXTURE_DIR/bad-pedagogy.json"
printf '%s\n' '[{"body": "<!-- trainer-codereview-toebeans-feat-x -->\n<!-- head=abcdef0 verdict=APPROVE -->\n### Pedagogy\n\n1. x\n"}]' >"$bad_ped"
expect_fail "Pedagogy heading rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$bad_ped" \
  bash "$GATE" 1 abcdef0123456789abcdef0123456789abcdef0 feat/x weijia-89/toebeans

stale="$FIXTURE_DIR/stale.json"
printf '%s\n' '[{"body": "<!-- trainer-codereview-toebeans-feat-x -->\n<!-- head=0000000 verdict=APPROVE -->\n### Trainer notes\n1. **Program notes:** x\n2. **Your form:** x\n3. **Next session:** x\n"}]' >"$stale"
expect_fail "stale head rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$stale" \
  bash "$GATE" 1 abcdef0123456789abcdef0123456789abcdef0 feat/x weijia-89/toebeans

empty="$FIXTURE_DIR/empty.json"
printf '%s\n' '[]' >"$empty"
expect_fail "missing comment rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$empty" \
  bash "$GATE" 1 abcdef0 feat/x weijia-89/toebeans

theater="$FIXTURE_DIR/theater.json"
theater_body=$(python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' \
  <"$ROOT/tests/trainer_codereview/fixtures/round1_theater_bad.md")
printf '[{"body": %s}]\n' "$theater_body" >"$theater"
expect_fail "round1 theater APPROVE rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$theater" \
  bash "$GATE" 20 1d6ed94c335fb32197c75fef5c34c163a95c09e4 feature/autonomous-code-review weijia-89/trainer.skill

r6_bad_comment_fixed="$FIXTURE_DIR/r6-bad.json"
python3 - "$ROOT" "$r6_bad_comment_fixed" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
review = (root / "tests/trainer_codereview/fixtures/r6_review_no_closure.md").read_text()
body = (
    "<!-- trainer-codereview-trainer.skill-feature-autonomous-code-review -->\n"
    "<!-- head=abcdef0 verdict=APPROVE round=1 -->\n"
    + review
)
out.write_text(json.dumps([{"body": body}]), encoding="utf-8")
PY
expect_fail "R-6 code without docs rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$r6_bad_comment_fixed" \
  TRAINER_PR_REVIEW_FILES_FIXTURE="$ROOT/tests/trainer_codereview/fixtures/r6_files_code_no_docs.txt" \
  bash "$GATE" 20 abcdef0123456789abcdef0123456789abcdef0 feature/autonomous-code-review weijia-89/trainer.skill

expect_fail "PR body grep-only checks rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$good" \
  TRAINER_PR_BODY_FILE="$ROOT/tests/trainer_codereview/fixtures/pr_body_weak_checks.md" \
  bash "$GATE" 99 805402b886b160d3acaf9130cba1363edb1a4d7e feat/style-lab-compose-alignment weijia-89/toebeans

expect_pass "PR body real-harness checks accepted" \
  env TRAINER_PR_REVIEW_FIXTURE="$good" \
  TRAINER_PR_BODY_FILE="$ROOT/tests/trainer_codereview/fixtures/pr_body_good.md" \
  bash "$GATE" 99 805402b886b160d3acaf9130cba1363edb1a4d7e feat/style-lab-compose-alignment weijia-89/toebeans

expect_fail "PR body missing Test plan rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$good" \
  TRAINER_PR_BODY_FILE="$ROOT/tests/trainer_codereview/fixtures/pr_body_missing_test_plan.md" \
  bash "$GATE" 99 805402b886b160d3acaf9130cba1363edb1a4d7e feat/style-lab-compose-alignment weijia-89/toebeans

expect_fail "PR body unavailable rejected" \
  env TRAINER_PR_REVIEW_FIXTURE="$good" \
  TRAINER_PR_BODY_FILE="$FIXTURE_DIR/missing-pr-body.md" \
  bash "$GATE" 99 805402b886b160d3acaf9130cba1363edb1a4d7e feat/style-lab-compose-alignment weijia-89/toebeans

echo "All ci-trainer-pr-review-gate self-tests passed."
