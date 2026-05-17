#!/usr/bin/env bash
# verify_trainer_sync.sh
#
# Asserts that the four sync targets for the `trainer` skill are consistent:
#
#   1. ~/Projects/trainer.skill/SKILL.md           (canonical)
#   2. ~/.claude/skills/trainer/SKILL.md            (Claude mirror, byte-identical to canonical)
#   3. ~/Projects/.cursor/rules/trainer.mdc         (Cursor trigger, references canonical path)
#   4. ~/Projects/.windsurf/rules/trainer.md        (Windsurf trigger, references canonical path)
#
# Run from anywhere. Exits 0 on success, nonzero on any invariant violation.
# Prints concrete failure detail. Never modifies any of the four files.

set -euo pipefail

CANONICAL="$HOME/Projects/trainer.skill/SKILL.md"
CLAUDE="$HOME/.claude/skills/trainer/SKILL.md"
CURSOR="$HOME/Projects/.cursor/rules/trainer.mdc"
WINDSURF="$HOME/Projects/.windsurf/rules/trainer.md"

FAIL=0

# Existence checks
for path in "$CANONICAL" "$CLAUDE" "$CURSOR" "$WINDSURF"; do
  if [[ ! -f "$path" ]]; then
    echo "FAIL  missing: $path"
    FAIL=1
  fi
done

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi

# Invariant 1: canonical and Claude mirror are byte-identical
if ! diff -q "$CANONICAL" "$CLAUDE" >/dev/null; then
  echo "FAIL  canonical and Claude mirror diverge:"
  echo "      $CANONICAL"
  echo "      $CLAUDE"
  diff "$CANONICAL" "$CLAUDE" | head -40 | sed 's/^/        /'
  FAIL=1
else
  echo "PASS  canonical ≡ Claude mirror (byte-identical)"
fi

# Invariant 2: Cursor trigger references the canonical absolute path
if ! grep -q "$CANONICAL" "$CURSOR"; then
  echo "FAIL  Cursor trigger does not reference canonical path: $CANONICAL"
  echo "      (checked in $CURSOR)"
  FAIL=1
else
  echo "PASS  Cursor trigger references canonical path"
fi

# Invariant 3: Windsurf trigger references the canonical absolute path
if ! grep -q "$CANONICAL" "$WINDSURF"; then
  echo "FAIL  Windsurf trigger does not reference canonical path: $CANONICAL"
  echo "      (checked in $WINDSURF)"
  FAIL=1
else
  echo "PASS  Windsurf trigger references canonical path"
fi

# Invariant 4: all four files agree on the version string
CANONICAL_VERSION=$(grep -m1 '^version:' "$CANONICAL" | awk '{print $2}')
CLAUDE_VERSION=$(grep -m1 '^version:' "$CLAUDE" | awk '{print $2}')
CURSOR_VERSION=$(grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' "$CURSOR" | head -1 | tr -d 'v')
WINDSURF_VERSION=$(grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' "$WINDSURF" | head -1 | tr -d 'v')

if [[ "$CANONICAL_VERSION" != "$CLAUDE_VERSION" ]]; then
  echo "FAIL  version mismatch canonical=$CANONICAL_VERSION claude=$CLAUDE_VERSION"
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
  echo "PASS  all four sync targets agree on version $CANONICAL_VERSION"
fi

# Invariant 5: SKILL.md (canonical) is ≤180 lines (bootstrap-skill cap; bumped in v0.5.0 for Red Flags / Rationalizations sections; original 100, bumped to 140 in v0.4.0, then to 180 in v0.5.0)
CANONICAL_LINES=$(wc -l < "$CANONICAL")
if [[ "$CANONICAL_LINES" -gt 180 ]]; then
  echo "WARN  canonical SKILL.md is $CANONICAL_LINES lines (soft cap 180)"
fi

# Invariant 6: zero em-dashes (Wei's writing-style hard rule, 2026-05-15)
EMDASH_FAIL=0
for path in "$CANONICAL" "$CLAUDE" "$CURSOR" "$WINDSURF"; do
  count=$(grep -c "—" "$path" 2>/dev/null) || count=0
  if [[ "$count" -gt 0 ]]; then
    echo "FAIL  $count em-dash(es) found in $path (hard rule: zero em-dashes)"
    FAIL=1
    EMDASH_FAIL=1
  fi
done
if [[ "$EMDASH_FAIL" -eq 0 ]]; then
  echo "PASS  zero em-dashes in all four sync targets"
fi

# Invariant 7: Cursor trigger is alwaysApply:true; Windsurf trigger is always_on
if ! grep -q "^alwaysApply: true" "$CURSOR"; then
  echo "FAIL  Cursor trigger missing 'alwaysApply: true' (trainer must be always-on)"
  FAIL=1
else
  echo "PASS  Cursor trigger is alwaysApply: true"
fi
if ! grep -q "^trigger: always_on" "$WINDSURF"; then
  echo "FAIL  Windsurf trigger missing 'trigger: always_on' (trainer must be always-on)"
  FAIL=1
else
  echo "PASS  Windsurf trigger is always_on"
fi

# Invariant 8: zero private-path leaks in the trainer.skill repo (everything that
# gets pushed to the public github mirror). Catches accidental references to
# private review docs, career-help workspace, or local-only directories before
# they ship. Added 2026-05-16 after two consecutive sanitization passes.
REPO_ROOT="$HOME/Projects/trainer.skill"
LEAK_PATTERN='(/Users/wjia/|~/Projects/(reviews|career-help|local[-_]?only)/)'
SELF_BASENAME="$(basename "${BASH_SOURCE[0]}")"

if command -v git >/dev/null 2>&1 && [[ -d "$REPO_ROOT/.git" ]]; then
  # Collect tracked files, excluding this verify script (which contains the
  # patterns by necessity) and the CHANGELOG (which documents past sanitization
  # work and may reference the patterns in prose).
  mapfile -t TRACKED_FILES < <(
    git -C "$REPO_ROOT" ls-files \
      | grep -v "^scripts/$SELF_BASENAME\$" \
      | sed "s|^|$REPO_ROOT/|"
  )
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

if [[ "$FAIL" -ne 0 ]]; then
  echo ""
  echo "VERDICT: FAIL ($FAIL invariant(s) violated)"
  exit 1
fi

echo ""
echo "VERDICT: PASS"
