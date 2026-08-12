#!/usr/bin/env bash
# install_hooks.sh -- install the local git pre-push hook that runs
# verify_trainer_sync.sh before every push. The hook lives in .git/hooks/
# (not tracked by git), so each clone must run this script once.
#
# Idempotent: safe to re-run; replaces any existing hook with the canonical
# one. Use `--uninstall` to remove the hook.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_PATH="$HOOKS_DIR/pre-push"

if [[ "${1:-}" == "--uninstall" ]]; then
  if [[ -f "$HOOK_PATH" ]]; then
    rm -f "$HOOK_PATH"
    echo "removed: $HOOK_PATH"
  else
    echo "no hook installed at $HOOK_PATH"
  fi
  exit 0
fi

if [[ ! -d "$REPO_ROOT/.git" ]]; then
  echo "error: $REPO_ROOT is not a git working tree" >&2
  exit 1
fi

mkdir -p "$HOOKS_DIR"

cat > "$HOOK_PATH" <<'HOOK'
#!/usr/bin/env bash
# pre-push: run verify_trainer_sync.sh and check_pr_merged before allowing a push. Blocks the
# push if any invariant fails or the branch has a merged PR.
# Bypass with --no-verify if absolutely necessary.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
"$SCRIPT_DIR/scripts/verify_trainer_sync.sh"
"$SCRIPT_DIR/scripts/check_pr_merged.sh"
HOOK

chmod +x "$HOOK_PATH"
echo "installed: $HOOK_PATH"
echo "Bypass once with: git push --no-verify"
