#!/usr/bin/env bash
# Print canonical emulator cold-start + launch blocks for trainer PR manual QA.
# Source of truth: references/trainer-github-pr-commentary.md
#
# Usage:
#   bash scripts/trainer_manual_test_block.sh buds
#   bash scripts/trainer_manual_test_block.sh toebeans
#   bash scripts/trainer_manual_test_block.sh buds --scenario settings-how-buds-works
#
set -euo pipefail

STACK=${1:-}
SCENARIO=""
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenario)
      SCENARIO=${2:-}
      shift 2
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$STACK" ]]; then
  echo "usage: $0 buds|toebeans [--scenario name]" >&2
  exit 2
fi

# Normalize aliases before repo detection
case "$STACK" in
  flutter) STACK=buds ;;
  android|kmp) STACK=toebeans ;;
esac

_detect_cwd_repo() {
  local root
  root=$(git -C "${TRAINER_REPO_ROOT:-$PWD}" rev-parse --show-toplevel 2>/dev/null || true)
  [[ -z "$root" ]] && return 0
  case "$root" in
    */buds|*/buds-wt-*|*/buds/*) echo buds ;;
    */toebeans|*/toebeans-*|*/toebeans-worktrees/*|*/toebeans/*) echo toebeans ;;
    *) echo "" ;;
  esac
}

CWD_REPO=$(_detect_cwd_repo)
GIT_ROOT=$(git -C "${TRAINER_REPO_ROOT:-$PWD}" rev-parse --show-toplevel 2>/dev/null || true)
if [[ -n "$CWD_REPO" && "$CWD_REPO" != "$STACK" ]]; then
  echo "trainer_manual_test_block: stack '$STACK' does not match git root repo '$CWD_REPO' (${GIT_ROOT:-unknown})" >&2
  echo "  Run from the matching product repo, or pass the correct stack (buds|toebeans)." >&2
  exit 1
fi

_emulator_block() {
  cat <<'EOF'
#### Emulator — cold start (no device booted)

Assume **no** emulator running and **no** `flutter run` session.

1. **PATH (Android SDK tools):**
   ```bash
   export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"
   ```
2. **Launch AVD** (pick one):
   ```bash
   flutter emulators --launch toebeans-pixel7
   ```
   ```bash
   ~/Library/Android/sdk/emulator/emulator -avd toebeans-pixel7 &
   ```
3. **Wait until device is ready** (repeat until a device line appears):
   ```bash
   adb devices
   flutter devices
   ```
   Expect `emulator-5554` (or device id `toebeans-pixel7` in `flutter devices`).
EOF
}

_buds_launch() {
  cat <<'EOF'
4. **Run Buds on the emulator** (from repo root):
   ```bash
   cd ~/Projects/buds/app
   flutter run -d emulator-5554
   ```
   If `flutter devices` shows only `toebeans-pixel7`, use:
   ```bash
   flutter run -d toebeans-pixel7
   ```
EOF
}

_toebeans_launch() {
  cat <<'EOF'
4. **Install debug APK** (from repo root):
   ```bash
   cd ~/Projects/toebeans
   ./gradlew :androidApp:installDebug
   ```
5. **Launch main activity:**
   ```bash
   adb shell am start -n app.toebeans.android/.MainActivity
   ```
EOF
}

case "$STACK" in
  buds)
    _emulator_block
    _buds_launch
    case "$SCENARIO" in
      ""|"--scenario")
        ;;
      settings-how-buds-works)
        cat <<'EOF'

#### In-app — Settings → How Buds works (PR #41-shaped)

**Goal:** `/settings/how-buds-works` renders `HowBudsWorksPage` (`fromSettings: true`), not the placeholder.

6. Reach **garden home** (complete onboarding on fresh install, or use an already-onboarded emulator).
7. Tap the **weather strip** on garden home → **your state** (`/settings/state`).
8. Tap **pause** → on pause screen tap **rest for now** (or **tend again** if already paused) → lands on **settings** root (`/settings`).
9. Tap **how Buds works**.
10. **Expect:** Full S01d explainer (scrollable sections, plant icons). **Not** placeholder copy `S01d (from settings)`.
11. **Expect:** Bottom action shows **done** (settings mode), not onboarding **back** / scroll-to-continue CTA.
12. Tap **done** → returns to settings root.
EOF
        ;;
      *)
        echo "unknown buds scenario: $SCENARIO" >&2
        exit 2
        ;;
    esac
    ;;
  toebeans)
    _emulator_block
    _toebeans_launch
    ;;
  *)
    echo "usage: $0 buds|toebeans [--scenario name]" >&2
    exit 2
    ;;
esac
