#!/usr/bin/env bash
# Print canonical device cold-start + launch blocks for trainer PR manual QA.
# Buds: iOS-first; reads ~/Projects/buds/localonly/trainer/manual-testing-buds.md when present.
# Source: references/buds-manual-testing.md, references/trainer-github-pr-commentary.md
#
# Usage:
#   bash scripts/trainer_manual_test_block.sh buds [--platform ios|android|both] [--scenario name]
#   bash scripts/trainer_manual_test_block.sh toebeans
#
set -euo pipefail

STACK=${1:-}
PLATFORM=ios
SCENARIO=""
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      PLATFORM=${2:-}
      shift 2
      ;;
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
  echo "usage: $0 buds|toebeans [--platform ios|android|both] [--scenario name]" >&2
  exit 2
fi

case "$PLATFORM" in
  ios|android|both) ;;
  *)
    echo "usage: --platform must be ios, android, or both" >&2
    exit 2
    ;;
esac

# Normalize aliases before repo detection
case "$STACK" in
  flutter) STACK=buds ;;
  android|kmp) STACK=toebeans ;;
esac

BUDS_ROOT=${BUDS_ROOT:-$HOME/Projects/buds}
BUDS_MANUAL="${BUDS_ROOT}/localonly/trainer/manual-testing-buds.md"

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

# If invoked from buds checkout, prefer that tree for localonly reads
if [[ "$CWD_REPO" == buds && -n "$GIT_ROOT" ]]; then
  BUDS_ROOT=$GIT_ROOT
  BUDS_MANUAL="${BUDS_ROOT}/localonly/trainer/manual-testing-buds.md"
fi

_buds_extract_marked() {
  local start_tag="$1"
  local end_tag="$2"
  local file="$3"
  awk -v start="$start_tag" -v end="$end_tag" '
    $0 ~ start { found=1; next }
    $0 ~ end { found=0; next }
    found { print }
  ' "$file"
}

_buds_emit_from_localonly() {
  local want=$1
  if [[ ! -f "$BUDS_MANUAL" ]]; then
    return 1
  fi
  case "$want" in
    ios)
      _buds_extract_marked 'TRAINER_MANUAL_IOS_START' 'TRAINER_MANUAL_IOS_END' "$BUDS_MANUAL"
      ;;
    android)
      _buds_extract_marked 'TRAINER_MANUAL_ANDROID_START' 'TRAINER_MANUAL_ANDROID_END' "$BUDS_MANUAL"
      ;;
    both)
      _buds_emit_from_localonly ios
      echo
      _buds_emit_from_localonly android
      ;;
  esac
}

_buds_fallback_ios() {
  cat <<'EOF'
#### iOS Simulator — cold start (buds; copy-paste)

Assume **no** Simulator booted and **no** `flutter run` session. Default device: **iPhone 13** via in-repo scripts (see `.cursor/rules/ios-test-device.mdc`).

**Checkout + verify**

```bash
cd ~/Projects/buds
git checkout {branch}
git pull --ff-only origin {branch}
bash scripts/verify_buds.sh
```

**Cold start**

```bash
cd ~/Projects/buds/app
flutter pub get
UDID="$(bash scripts/boot_ios_test_sim.sh)"
flutter devices
flutter run -d "${UDID}"
```

One-liner: `cd ~/Projects/buds/app && bash scripts/run_ios.sh`

**Fresh install (before each scenario)**

```bash
cd ~/Projects/buds/app
UDID="$(bash scripts/boot_ios_test_sim.sh)"
xcrun simctl uninstall "${UDID}" io.github.weijia89.buds
flutter run -d "${UDID}"
```

Then numbered **in-app** steps (routes, expected copy).

**Forbidden on buds PRs:** `./gradlew`, `:androidApp:installDebug`, `app.toebeans.android`, toebeans launch paths.
EOF
}

_buds_fallback_android() {
  cat <<'EOF'
#### Android emulator — optional (buds)

1. `export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"`
2. `flutter emulators --launch buds-pixel7` (or `emulator -avd buds-pixel7 &`)
3. Wait: `adb devices` and `flutter devices` show a device id (e.g. `emulator-5554`).
4. `cd ~/Projects/buds/app && flutter run -d emulator-5554`
5. Fresh install: `adb shell pm clear io.github.weijia_89.buds`
EOF
}

_buds_emit_platform() {
  local want=$1
  if _buds_emit_from_localonly "$want" 2>/dev/null; then
    return 0
  fi
  case "$want" in
    ios) _buds_fallback_ios ;;
    android) _buds_fallback_android ;;
    both)
      _buds_fallback_ios
      echo
      _buds_fallback_android
      ;;
  esac
}

_emulator_block_toebeans() {
  cat <<'EOF'
#### Emulator — cold start (no device booted)

Assume **no** emulator running. Copy-paste **all** of steps 1–6 before in-app scenarios.

1. **JDK 17** (required for `./gradlew`; Homebrew is not visible to `/usr/libexec/java_home` unless symlinked):
   ```bash
   for _jdk in \
     /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
     /usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home; do
     [[ -x "$_jdk/bin/java" ]] && export JAVA_HOME="$_jdk" && break
   done
   if [[ -z "${JAVA_HOME:-}" ]]; then
     echo "JDK 17 not found. Run: brew install openjdk@17" >&2
     exit 1
   fi
   export PATH="$JAVA_HOME/bin:$PATH"
   ```
2. **Android SDK** (`adb` + emulator; fixes `command not found: adb`):
   ```bash
   export ANDROID_HOME="$HOME/Library/Android/sdk"
   export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
   ```
3. **Launch AVD** (pick one):
   ```bash
   flutter emulators --launch toebeans-pixel7
   ```
   ```bash
   ~/Library/Android/sdk/emulator/emulator -avd toebeans-pixel7 &
   ```
4. **Wait until device is ready** (repeat until a device line appears):
   ```bash
   adb devices
   ```
   Expect `emulator-5554` with state `device`.
5. **Install debug APK** (from repo root):
   ```bash
   cd ~/Projects/toebeans
   ./gradlew :androidApp:installDebug
   ```
6. **Launch main activity:**
   ```bash
   adb shell am start -n app.toebeans.android/.MainActivity
   ```
EOF
}

_toebeans_launch() {
  : # steps 5–6 merged into _emulator_block_toebeans for one copy-paste block
}

case "$STACK" in
  buds)
    _buds_emit_platform "$PLATFORM"
    case "$SCENARIO" in
      ""|"--scenario")
        ;;
      settings-how-buds-works)
        cat <<'EOF'

#### In-app — Settings → How Buds works

**Goal:** `/settings/how-buds-works` renders `HowBudsWorksPage` (`fromSettings: true`), not the placeholder.

6. Reach **garden home** (complete onboarding on fresh install, or use an already-onboarded simulator).
7. Tap top-right **settings** (gear) → **settings** root (`/settings`). *(Requires PR that wires garden gear; not the pause detour.)*
8. Tap **how Buds works**.
9. **Expect:** Full S01d explainer (scrollable sections, plant icons). **Not** placeholder copy `S01d (from settings)`.
10. **Expect:** Bottom action shows **done** (settings mode), not onboarding **back** / scroll-to-continue CTA.
11. Tap **done** → returns to settings root.
EOF
        ;;
      *)
        echo "unknown buds scenario: $SCENARIO" >&2
        exit 2
        ;;
    esac
    ;;
  toebeans)
    if [[ "$PLATFORM" != ios ]]; then
      echo "trainer_manual_test_block: toebeans ignores --platform (Android only)" >&2
    fi
    _emulator_block_toebeans
    _toebeans_launch
    ;;
  *)
    echo "usage: $0 buds|toebeans [--platform ios|android|both] [--scenario name]" >&2
    exit 2
    ;;
esac
