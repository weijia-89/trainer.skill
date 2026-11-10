#!/usr/bin/env bash
# Guarded unit tests for scripts/check_changelog_drift.sh (ROADMAP Q3).
# Uses temp-dir git fixtures; no network.
set -euo pipefail

command -v git >/dev/null 2>&1 || { echo "FAIL: git not installed" >&2; exit 1; }
command -v command >/dev/null 2>&1 || true

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/check_changelog_drift.sh"
PASS=0
FAIL=0

pass() { echo "PASS  $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL  $1"; FAIL=$((FAIL + 1)); }

assert_exit() { # label expected actual
  if [[ "$2" == "$3" ]]; then
    pass "$1"
  else
    fail "$1 (expected exit $2, got $3)"
  fi
}

assert_contains() { # label haystack needle
  if printf '%s' "$2" | grep -Fq "$3"; then
    pass "$1"
  else
    fail "$1 (missing: $3)"
  fi
}

# Create a temp git repo with an initial commit (base).
make_repo() {
  local dir
  dir="$(mktemp -d)"
  git -C "$dir" init -q
  git -C "$dir" config user.email test@example.com
  git -C "$dir" config user.name test
  printf 'base\n' > "$dir/README.md"
  git -C "$dir" add README.md
  git -C "$dir" commit -qm base
  printf '%s' "$dir"
}

base_sha() {
  git -C "$1" rev-parse HEAD
}

run_drift() { # repo base_sha
  local repo="$1" base="$2"
  local out rc
  set +e
  out=$(cd "$repo"; BASE_SHA="$base" bash "$SCRIPT" 2>&1)
  rc=$?
  set -e
  printf '%s\n__RC__%s' "$out" "$rc"
}

# --- RED/GREEN behavior cases ---

# 1) FAIL when scripts/ changes without CHANGELOG.md
t1="$(make_repo)"
b1="$(base_sha "$t1")"
mkdir -p "$t1/scripts"
printf '#!/usr/bin/env bash\n' > "$t1/scripts/foo.sh"
git -C "$t1" add scripts/foo.sh
git -C "$t1" commit -qm 'add script'
r1="$(run_drift "$t1" "$b1")"
rc1="${r1##*__RC__}"; out1="${r1%$'\n'__RC__*}"
assert_exit "FAIL when scripts/ changes without CHANGELOG.md" "1" "$rc1"
assert_contains "scripts trigger message names rule" "$out1" "CHANGELOG.md"
assert_contains "scripts trigger message is actionable" "$out1" "scripts/"
rm -rf "$t1"

# 2) FAIL when SKILL.md changes without CHANGELOG.md
t2="$(make_repo)"
b2="$(base_sha "$t2")"
printf 'skill\n' > "$t2/SKILL.md"
git -C "$t2" add SKILL.md
git -C "$t2" commit -qm 'add skill'
r2="$(run_drift "$t2" "$b2")"
rc2="${r2##*__RC__}"; out2="${r2%$'\n'__RC__*}"
assert_exit "FAIL when SKILL.md changes without CHANGELOG.md" "1" "$rc2"
assert_contains "SKILL trigger message names rule" "$out2" "CHANGELOG.md"
assert_contains "SKILL trigger message names SKILL.md" "$out2" "SKILL.md"
rm -rf "$t2"

# 3) FAIL when tests/ changes without CHANGELOG.md
t3="$(make_repo)"
b3="$(base_sha "$t3")"
mkdir -p "$t3/tests"
printf 'test\n' > "$t3/tests/foo_test.sh"
git -C "$t3" add tests/foo_test.sh
git -C "$t3" commit -qm 'add test'
r3="$(run_drift "$t3" "$b3")"
rc3="${r3##*__RC__}"; out3="${r3%$'\n'__RC__*}"
assert_exit "FAIL when tests/ changes without CHANGELOG.md" "1" "$rc3"
assert_contains "tests trigger message names rule" "$out3" "CHANGELOG.md"
assert_contains "tests trigger message names tests/" "$out3" "tests/"
rm -rf "$t3"

# 4) PASS when triggering paths change AND CHANGELOG.md changes
t4="$(make_repo)"
b4="$(base_sha "$t4")"
mkdir -p "$t4/scripts"
printf 'x\n' > "$t4/scripts/foo.sh"
printf '## 2099-01-01\nentry\n' > "$t4/CHANGELOG.md"
git -C "$t4" add scripts/foo.sh CHANGELOG.md
git -C "$t4" commit -qm 'script + changelog'
r4="$(run_drift "$t4" "$b4")"
rc4="${r4##*__RC__}"
assert_exit "PASS when triggering path and CHANGELOG.md change" "0" "$rc4"
rm -rf "$t4"

# 5a) PASS on docs-only diff without CHANGELOG.md (R-6)
t5="$(make_repo)"
b5="$(base_sha "$t5")"
mkdir -p "$t5/references" "$t5/.github"
printf 'road\n' > "$t5/ROADMAP.md"
printf 'ctx\n' > "$t5/context.md"
printf 'ref\n' > "$t5/references/x.md"
printf 'name: x\n' > "$t5/.github/workflow.yml"
git -C "$t5" add ROADMAP.md context.md references/x.md .github/workflow.yml
git -C "$t5" commit -qm 'docs only'
r5="$(run_drift "$t5" "$b5")"
rc5="${r5##*__RC__}"
assert_exit "PASS docs-only diff without CHANGELOG.md (R-6)" "0" "$rc5"
rm -rf "$t5"

# 5b) PASS on docs-only diff with CHANGELOG.md present (R-6 allows it)
t6="$(make_repo)"
b6="$(base_sha "$t6")"
printf 'readme\n' > "$t6/README.md"
printf '## 2099-01-01\n' > "$t6/CHANGELOG.md"
git -C "$t6" add README.md CHANGELOG.md
git -C "$t6" commit -qm 'docs + changelog'
r6="$(run_drift "$t6" "$b6")"
rc6="${r6##*__RC__}"
assert_exit "PASS docs-only diff with CHANGELOG.md (R-6)" "0" "$rc6"
rm -rf "$t6"

echo ""
if [[ "$FAIL" -eq 0 ]]; then
  echo "OK test_check_changelog_drift ($PASS passed)"
  exit 0
else
  echo "FAILED test_check_changelog_drift ($FAIL failed, $PASS passed)" >&2
  exit 1
fi
