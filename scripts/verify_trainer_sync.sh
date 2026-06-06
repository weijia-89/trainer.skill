#!/usr/bin/env bash
# verify_trainer_sync.sh
#
# Asserts trainer skill sync targets (canonical SKILL.md + references/, Claude/Cursor/Windsurf mirrors):
#
#   1. ~/Projects/trainer.skill/SKILL.md           (canonical)
#   2. ~/.cursor/skills/trainer/SKILL.md            (Cursor mirror, byte-identical to canonical)
#   2b. ~/.cursor/skills/trainer/references/     (Cursor mirror, byte-identical to canonical references/)
#   3. ~/Projects/.cursor/rules/trainer.mdc         (Cursor trigger, references canonical path)
#   4. ~/Projects/trainer.skill/mirrors/windsurf-trainer.md  (Windsurf trigger template; optional install elsewhere)
#
# Run from anywhere. Exits 0 on success, nonzero on any invariant violation.
# Prints concrete failure detail. Syncs canonical SKILL.md + references/ into ~/.cursor/skills/trainer/, then asserts invariants.
# Troubleshooting: if ~/.cursor is a dangling symlink (e.g. target volume removed), local mirror sync fails.
#   Use GITHUB_ACTIONS=true GITHUB_WORKSPACE=$REPO_ROOT bash scripts/verify_trainer_sync.sh for repo-only checks,
#   or repoint ~/.cursor to a live directory before local verify (do not auto-repoint in CI/agents).
# Invariant 1b byte-identity (references/ mirror) is local-only; CI checks references/ presence + gate files.
# Authoritative 1b regression gate: full local verify here, or tests/trainer_sync/test_invariant_1b_references_mirror.sh.

set -euo pipefail

# Portable tracked-file list (macOS default bash 3.2 lacks mapfile).
collect_tracked_files() {
  local repo_root="$1" self_basename="$2"
  TRACKED_FILES=()
  while IFS= read -r relpath; do
    [[ -n "$relpath" ]] && TRACKED_FILES+=("$repo_root/$relpath")
  done < <(
    git -C "$repo_root" ls-files | grep -v "^scripts/$self_basename\$"
  )
}

# GitHub Actions has no local Claude/Cursor/Windsurf mirrors; run repo-only checks.
if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
  REPO_ROOT="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE unset in CI}"
  CANONICAL="$REPO_ROOT/SKILL.md"
  FAIL=0

  if [[ ! -f "$CANONICAL" ]]; then
    echo "FAIL  missing canonical SKILL.md at $CANONICAL"
    exit 1
  fi
  echo "PASS  canonical SKILL.md present"

  CANONICAL_PROMPT="$REPO_ROOT/prompts/trainer-codereview.txt"
  if [[ ! -f "$CANONICAL_PROMPT" ]]; then
    echo "FAIL  missing canonical agent prompt: $CANONICAL_PROMPT"
    FAIL=1
  else
    echo "PASS  canonical prompts/trainer-codereview.txt present"
  fi

  # sdk-review F1: CI repo-only path must guard references/ + mandatory gate files (Invariant 1b is local-only)
  CANONICAL_REFS="$REPO_ROOT/references"
  REQUIRED_REF_GATES=(
    trainer-pre-action-gates.md
    trainer-dispatch-gates.md
    trainer-runtime-compactness.md  # sdk-review F1: SKILL.md lazy-load target; CI must fail if deleted
    trainer-github-pr-commentary.md  # PR body test plans + Trainer notes on comments
    trainer-codereview.md
    trainer-contract-surfaces.md
    trainer-codereview-gate.md
    trainer-epistemic-layers.md
  )
  if [[ ! -d "$CANONICAL_REFS" ]]; then
    echo "FAIL  missing canonical references/: $CANONICAL_REFS"
    FAIL=1
  else
    echo "PASS  canonical references/ present"
    for gate in "${REQUIRED_REF_GATES[@]}"; do
      if [[ ! -f "$CANONICAL_REFS/$gate" ]]; then
        echo "FAIL  missing required reference gate file: $gate"
        FAIL=1
      fi
    done
    if [[ "$FAIL" -eq 0 ]]; then
      echo "PASS  required reference gate files present"
    fi
  fi

  SELF_BASENAME="$(basename "${BASH_SOURCE[0]}")"
  collect_tracked_files "$REPO_ROOT" "$SELF_BASENAME"
  LEAK_PATTERN='(/Users/wjia/|~/Projects/(reviews|career-help|toren|local[-_]?only)/)'
  if [[ ${#TRACKED_FILES[@]} -gt 0 ]]; then
    LEAK_REPORT=$(grep -HnE "$LEAK_PATTERN" "${TRACKED_FILES[@]}" 2>/dev/null || true)
    if [[ -n "$LEAK_REPORT" ]]; then
      LEAK_COUNT=$(printf '%s\n' "$LEAK_REPORT" | grep -c .)
      echo "FAIL  $LEAK_COUNT private-path leak(s) found in tracked files:"
      printf '%s\n' "$LEAK_REPORT" | head -20 | sed 's/^/        /'
      if [[ "$LEAK_COUNT" -gt 20 ]]; then
        echo "        ... ($((LEAK_COUNT - 20)) more)"
      fi
      FAIL=1
    else
      echo "PASS  zero private-path leaks across $REPO_ROOT tracked files"
    fi
  fi


  # Invariant (CI): root SKILL.md context budget (see tests/context_budget/budget.toml)
  CONTEXT_BUDGET="$REPO_ROOT/tests/context_budget/check_context_budget.py"
  if [[ -f "$CONTEXT_BUDGET" ]]; then
    set +e
    CB_OUT=$(python3 "$CONTEXT_BUDGET" 2>&1)
    CB_EXIT=$?
    set -e
    if [[ $CB_EXIT -ne 0 ]]; then
      echo "FAIL  context budget check exited $CB_EXIT:"
      printf '%s\n' "$CB_OUT" | sed 's/^/        /'
      FAIL=1
    else
      echo "PASS  context budget check"
    fi
  else
    echo "WARN  skipping context budget check (missing $CONTEXT_BUDGET)"
  fi

  # sdk-review F2: unit tests guard load_budget, warn-only exit paths, snapshot drift
  CONTEXT_BUDGET_TESTS="$REPO_ROOT/tests/context_budget/test_check_context_budget.py"
  if [[ -f "$CONTEXT_BUDGET_TESTS" ]]; then
    set +e
    CBT_OUT=$(python3 "$CONTEXT_BUDGET_TESTS" 2>&1)
    CBT_EXIT=$?
    set -e
    if [[ $CBT_EXIT -ne 0 ]]; then
      echo "FAIL  context budget unit tests exited $CBT_EXIT:"
      printf '%s\n' "$CBT_OUT" | sed 's/^/        /'
      FAIL=1
    else
      echo "PASS  context budget unit tests"
    fi
  else
    echo "WARN  skipping context budget unit tests (missing $CONTEXT_BUDGET_TESTS)"
  fi

  # sdk-review F2: temp-dir fixture guards Invariant 1b rsync + per-file diff loop (local mirror N/A in CI)
  INVARIANT_1B_TEST="$REPO_ROOT/tests/trainer_sync/test_invariant_1b_references_mirror.sh"
  if [[ -f "$INVARIANT_1B_TEST" ]]; then
    set +e
    I1B_OUT=$(bash "$INVARIANT_1B_TEST" 2>&1)
    I1B_EXIT=$?
    set -e
    if [[ $I1B_EXIT -ne 0 ]]; then
      echo "FAIL  invariant 1b references mirror fixture exited $I1B_EXIT:"
      printf '%s\n' "$I1B_OUT" | sed 's/^/        /'
      FAIL=1
    else
      echo "PASS  invariant 1b references mirror fixture"
    fi
  else
    echo "WARN  skipping invariant 1b fixture (missing $INVARIANT_1B_TEST)"
  fi

  if [[ "$FAIL" -ne 0 ]]; then
    echo ""
    echo "VERDICT: FAIL (CI repo-only checks)"
    exit 1
  fi

  echo ""
  echo "VERDICT: PASS (CI repo-only checks)"
  exit 0
fi

REPO_ROOT="$HOME/Projects/trainer.skill"
CANONICAL="$REPO_ROOT/SKILL.md"
CURSOR_SKILL="$HOME/.cursor/skills/trainer/SKILL.md"
CURSOR="$HOME/Projects/.cursor/rules/trainer.mdc"
WINDSURF_MIRROR="$REPO_ROOT/mirrors/windsurf-trainer.md"
WINDSURF_INSTALL="${WINDSURF_INSTALL:-$HOME/Projects/.windsurf/rules/trainer.md}"

if [[ -L "$HOME/.cursor" ]] && [[ ! -e "$HOME/.cursor" ]]; then
  echo "FAIL  ~/.cursor is a dangling symlink (target missing); cannot sync Cursor mirror"
  echo "      Repoint ~/.cursor to a live directory, or run repo-only verify:"
  echo "      GITHUB_ACTIONS=true GITHUB_WORKSPACE=$REPO_ROOT bash scripts/verify_trainer_sync.sh"
  exit 1
fi

FAIL=0
CANONICAL_REFS="$REPO_ROOT/references"
CURSOR_REFS="$HOME/.cursor/skills/trainer/references"

# sdk-review F1: guard canonical references/ before rsync; set -e aborts on missing source otherwise
if [[ ! -d "$CANONICAL_REFS" ]]; then
  echo "FAIL  missing canonical references/: $CANONICAL_REFS"
  exit 1
fi

# Mirror sync: Cursor skill tree must include references/ for mandatory file_read overlays (post #4 P2)
mkdir -p "$(dirname "$CURSOR_SKILL")" "$CURSOR_REFS"
rsync -a --delete "$CANONICAL_REFS/" "$CURSOR_REFS/"
if ! diff -q "$CANONICAL" "$CURSOR_SKILL" >/dev/null 2>&1; then
  cp "$CANONICAL" "$CURSOR_SKILL"
fi

# Existence checks
for path in "$CANONICAL" "$CURSOR_SKILL" "$CURSOR" "$WINDSURF_MIRROR"; do
  if [[ ! -f "$path" ]]; then
    echo "FAIL  missing: $path"
    FAIL=1
  fi
done

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi

# Invariant 1: canonical and Cursor skills mirror are byte-identical
if ! diff -q "$CANONICAL" "$CURSOR_SKILL" >/dev/null; then
  echo "FAIL  canonical and Cursor skills mirror diverge:"
  echo "      $CANONICAL"
  echo "      $CURSOR_SKILL"
  diff "$CANONICAL" "$CURSOR_SKILL" | head -40 | sed 's/^/        /'
  FAIL=1
else
  echo "PASS  canonical ≡ Cursor skills mirror (byte-identical)"
fi

# Invariant 1b: canonical references/ ≡ Cursor skills mirror (byte-identical per file)
# sdk-review F4: canonical refs guard runs once before rsync (lines 152–156 above); no duplicate check here
if [[ ! -d "$CURSOR_REFS" ]]; then
  echo "FAIL  missing Cursor references mirror: $CURSOR_REFS"
  FAIL=1
else
  REF_FAIL=0
  while IFS= read -r -d '' ref_file; do
    rel="${ref_file#"$CANONICAL_REFS"/}"
    cursor_file="$CURSOR_REFS/$rel"
    if [[ ! -f "$cursor_file" ]] || ! diff -q "$ref_file" "$cursor_file" >/dev/null; then
      echo "FAIL  references mirror diverge: $rel"
      REF_FAIL=1
    fi
  done < <(find "$CANONICAL_REFS" -type f -print0)
  if [[ "$REF_FAIL" -ne 0 ]]; then
    FAIL=1
  else
    echo "PASS  canonical references/ ≡ Cursor skills mirror (byte-identical)"
  fi
fi

# Invariant 2: Cursor trigger references the canonical absolute path
if ! grep -q "$CANONICAL" "$CURSOR"; then
  echo "FAIL  Cursor trigger does not reference canonical path: $CANONICAL"
  echo "      (checked in $CURSOR)"
  FAIL=1
else
  echo "PASS  Cursor trigger references canonical path"
fi

# Invariant 3: Windsurf template references the canonical path (absolute or ~/Projects/)
if ! grep -qE '(~/Projects/trainer\.skill/SKILL\.md|/Projects/trainer\.skill/SKILL\.md)' "$WINDSURF_MIRROR"; then
  echo "FAIL  Windsurf template does not reference canonical trainer.skill/SKILL.md"
  echo "      (checked in $WINDSURF_MIRROR)"
  FAIL=1
else
  echo "PASS  Windsurf template references canonical path"
fi

if [[ -f "$WINDSURF_INSTALL" ]]; then
  if ! diff -q "$WINDSURF_MIRROR" "$WINDSURF_INSTALL" >/dev/null 2>&1; then
    echo "WARN  optional Windsurf install diverges from mirrors/windsurf-trainer.md"
    echo "      install: $WINDSURF_INSTALL"
    echo "      fix: cp \"$WINDSURF_MIRROR\" \"$WINDSURF_INSTALL\""
  else
    echo "PASS  optional Windsurf install matches template"
  fi
else
  echo "PASS  no Windsurf install at $WINDSURF_INSTALL (template-only OK)"
fi

# Invariant 4: SKILL.md + IDE triggers agree on version string (not references/ tree; see header 2b)
CANONICAL_VERSION=$(grep -m1 '^version:' "$CANONICAL" | awk '{print $2}')
CURSOR_SKILL_VERSION=$(grep -m1 '^version:' "$CURSOR_SKILL" | awk '{print $2}')
CURSOR_VERSION=$(grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' "$CURSOR" | head -1 | tr -d 'v')
WINDSURF_VERSION=$(grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' "$WINDSURF_MIRROR" | head -1 | tr -d 'v')

if [[ "$CANONICAL_VERSION" != "$CURSOR_SKILL_VERSION" ]]; then
  echo "FAIL  version mismatch canonical=$CANONICAL_VERSION cursor_skill=$CURSOR_SKILL_VERSION"
  FAIL=1
fi
if [[ "$CANONICAL_VERSION" != "$CURSOR_VERSION" ]]; then
  echo "FAIL  version mismatch canonical=$CANONICAL_VERSION cursor=$CURSOR_VERSION"
  FAIL=1
fi
if [[ "$CANONICAL_VERSION" != "$WINDSURF_VERSION" ]]; then
  echo "FAIL  version mismatch canonical=$CANONICAL_VERSION windsurf=$WINDSURF_VERSION"
  FAIL=1
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo "PASS  SKILL.md + IDE triggers agree on version $CANONICAL_VERSION"
fi

# Invariant 5: SKILL.md (canonical) is ≤360 lines (bootstrap-skill cap; v0.11.0 compact router is ~136 lines; token/line budget enforced in Invariant 11)
CANONICAL_LINES=$(wc -l < "$CANONICAL")
if [[ "$CANONICAL_LINES" -gt 360 ]]; then
  echo "WARN  canonical SKILL.md is $CANONICAL_LINES lines (soft cap 360)"
fi

# Invariant 6: zero em-dashes (Wei's writing-style hard rule, 2026-05-15)
EMDASH_FAIL=0
for path in "$CANONICAL" "$CURSOR_SKILL" "$CURSOR" "$WINDSURF_MIRROR"; do
  count=$(grep -c "—" "$path" 2>/dev/null) || count=0
  if [[ "$count" -gt 0 ]]; then
    echo "FAIL  $count em-dash(es) found in $path (hard rule: zero em-dashes)"
    FAIL=1
    EMDASH_FAIL=1
  fi
done
if [[ "$EMDASH_FAIL" -eq 0 ]]; then
  echo "PASS  zero em-dashes in all SKILL/trigger sync targets"
fi

# Invariant 7: Cursor trigger is alwaysApply:true; Windsurf trigger is always_on
if ! grep -q "^alwaysApply: true" "$CURSOR"; then
  echo "FAIL  Cursor trigger missing 'alwaysApply: true' (trainer must be always-on)"
  FAIL=1
else
  echo "PASS  Cursor trigger is alwaysApply: true"
fi
if ! grep -q "^trigger: always_on" "$WINDSURF_MIRROR"; then
  echo "FAIL  Windsurf template missing 'trigger: always_on' (trainer must be always-on)"
  FAIL=1
else
  echo "PASS  Windsurf template is always_on"
fi

# Invariant 8: zero private-path leaks in the trainer.skill repo (everything that
# gets pushed to the public github mirror). Catches accidental references to
# private review docs, career-help workspace (renamed to toren/ 2026-05-19, both
# names kept in pattern for transition safety), or local-only directories before
# they ship. Added 2026-05-16 after two consecutive sanitization passes.
LEAK_PATTERN='(/Users/wjia/|~/Projects/(reviews|career-help|toren|local[-_]?only)/)'
SELF_BASENAME="$(basename "${BASH_SOURCE[0]}")"

if command -v git >/dev/null 2>&1 && [[ -d "$REPO_ROOT/.git" ]]; then
  collect_tracked_files "$REPO_ROOT" "$SELF_BASENAME"
  if [[ ${#TRACKED_FILES[@]} -gt 0 ]]; then
    LEAK_REPORT=$(grep -HnE "$LEAK_PATTERN" "${TRACKED_FILES[@]}" 2>/dev/null || true)
    if [[ -n "$LEAK_REPORT" ]]; then
      LEAK_COUNT=$(printf '%s\n' "$LEAK_REPORT" | grep -c .)
      echo "FAIL  $LEAK_COUNT private-path leak(s) found in tracked files:"
      printf '%s\n' "$LEAK_REPORT" | head -20 | sed 's/^/        /'
      if [[ "$LEAK_COUNT" -gt 20 ]]; then
        echo "        ... ($((LEAK_COUNT - 20)) more)"
      fi
      FAIL=1
    else
      echo "PASS  zero private-path leaks across $REPO_ROOT tracked files"
    fi
  fi
else
  echo "WARN  skipping private-path leak scan (git unavailable or repo not initialized)"
fi

# Invariant 9: superset falsifier harness exits 0 (Mozilla-mythos regression gate).
# Added 2026-05-19 as part of superset v0.4.0 manifest-harness Phase 2 ship.
# Runs against the canonical superset.skill harness; the trainer bundle rsyncs
# from canonical, so canonical-pass implies bundle-pass when bundle is fresh.
# If the harness script is missing, log WARN and skip rather than FAIL — trainer
# can theoretically release without superset present, though current bundle ships it.
SUPERSET_HARNESS="$HOME/Projects/superset.skill/scripts/falsifier-harness/run-all.sh"
if [[ -f "$SUPERSET_HARNESS" ]]; then
  # Suspend errexit so a harness failure does not short-circuit the FAIL-block
  # diagnostic output. Re-enable immediately after capturing the exit code.
  set +e
  HARNESS_OUTPUT=$(bash "$SUPERSET_HARNESS" 2>&1)
  HARNESS_EXIT=$?
  set -e
  if [[ "$HARNESS_EXIT" -ne 0 ]]; then
    echo "FAIL  superset falsifier harness exited $HARNESS_EXIT (expected 0):"
    printf '%s\n' "$HARNESS_OUTPUT" | head -30 | sed 's/^/        /'
    FAIL=1
  else
    HARNESS_PASS_COUNT=$(printf '%s\n' "$HARNESS_OUTPUT" | grep -c '^PASS ')
    echo "PASS  superset falsifier harness: $HARNESS_PASS_COUNT hypotheses verified"
  fi
else
  echo "WARN  skipping superset falsifier harness invariant (script not present at $SUPERSET_HARNESS)"
fi

# Invariant 10: superset prompt-level harness exits 0 (added 2026-05-19 as part of
# superset v0.6.0 ship). Validates agent prompts against H5 (worktree first command)
# across three shapes (worktree, same-tree exception, no-git exception). If the script
# is missing, log WARN and skip rather than FAIL.
SUPERSET_PROMPT_HARNESS="$HOME/Projects/superset.skill/scripts/prompt-level-harness/run-all.sh"
if [[ -f "$SUPERSET_PROMPT_HARNESS" ]]; then
  set +e
  PROMPT_HARNESS_OUTPUT=$(bash "$SUPERSET_PROMPT_HARNESS" 2>&1)
  PROMPT_HARNESS_EXIT=$?
  set -e
  if [[ "$PROMPT_HARNESS_EXIT" -ne 0 ]]; then
    echo "FAIL  superset prompt-level harness exited $PROMPT_HARNESS_EXIT (expected 0):"
    printf '%s\n' "$PROMPT_HARNESS_OUTPUT" | head -30 | sed 's/^/        /'
    FAIL=1
  else
    PROMPT_HARNESS_PASS_COUNT=$(printf '%s\n' "$PROMPT_HARNESS_OUTPUT" | grep -c '^PASS ')
    echo "PASS  superset prompt-level harness: $PROMPT_HARNESS_PASS_COUNT fixtures verified"
  fi
else
  echo "WARN  skipping superset prompt-level harness invariant (script not present at $SUPERSET_PROMPT_HARNESS)"
fi


# Invariant 11: root SKILL.md context budget (tests/context_budget/budget.toml)
CONTEXT_BUDGET="$REPO_ROOT/tests/context_budget/check_context_budget.py"
if [[ -f "$CONTEXT_BUDGET" ]]; then
  set +e
  CB_OUT=$(python3 "$CONTEXT_BUDGET" 2>&1)
  CB_EXIT=$?
  set -e
  if [[ $CB_EXIT -ne 0 ]]; then
    echo "FAIL  context budget check exited $CB_EXIT:"
    printf '%s\n' "$CB_OUT" | sed 's/^/        /'
    FAIL=1
  else
    echo "PASS  context budget check"
  fi
else
  echo "WARN  skipping context budget check (missing $CONTEXT_BUDGET)"
fi

# sdk-review F2: unit tests guard load_budget, warn-only exit paths, snapshot drift
CONTEXT_BUDGET_TESTS="$REPO_ROOT/tests/context_budget/test_check_context_budget.py"
if [[ -f "$CONTEXT_BUDGET_TESTS" ]]; then
  set +e
  CBT_OUT=$(python3 "$CONTEXT_BUDGET_TESTS" 2>&1)
  CBT_EXIT=$?
  set -e
  if [[ $CBT_EXIT -ne 0 ]]; then
    echo "FAIL  context budget unit tests exited $CBT_EXIT:"
    printf '%s\n' "$CBT_OUT" | sed 's/^/        /'
    FAIL=1
  else
    echo "PASS  context budget unit tests"
  fi
else
  echo "WARN  skipping context budget unit tests (missing $CONTEXT_BUDGET_TESTS)"
fi

# sdk-review F2: temp-dir fixture guards Invariant 1b rsync + per-file diff loop
INVARIANT_1B_TEST="$REPO_ROOT/tests/trainer_sync/test_invariant_1b_references_mirror.sh"
if [[ -f "$INVARIANT_1B_TEST" ]]; then
  set +e
  I1B_OUT=$(bash "$INVARIANT_1B_TEST" 2>&1)
  I1B_EXIT=$?
  set -e
  if [[ $I1B_EXIT -ne 0 ]]; then
    echo "FAIL  invariant 1b references mirror fixture exited $I1B_EXIT:"
    printf '%s\n' "$I1B_OUT" | sed 's/^/        /'
    FAIL=1
  else
    echo "PASS  invariant 1b references mirror fixture"
  fi
else
  echo "WARN  skipping invariant 1b fixture (missing $INVARIANT_1B_TEST)"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo ""
  echo "VERDICT: FAIL ($FAIL invariant(s) violated)"
  exit 1
fi

echo ""
echo "VERDICT: PASS"
