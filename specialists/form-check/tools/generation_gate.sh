#!/usr/bin/env bash
# generation_gate.sh — validates bash scripts for generation-time safety
#
# Usage:
#   bash generation_gate.sh [--strict] [--no-shellcheck] [file.sh ...]
#
# Philosophy: spirit over letter. We check for the presence of safeguards,
# not exact formatting. A script that handles errors well passes; one that
# silently fails does not.
#
# Checks:
#   1. Safety header: set -euo pipefail or equivalent error handling
#   2. No env collisions: avoid reserved env var names for local vars
#   3. Numeric validation: --flag N patterns should validate N
#   4. Tool checks: external tools should have existence checks or graceful fallback
#   5. Test co-existence: matching test file exists (warn in default, fail in strict)
#   6. shellcheck: pass if available (warn in default, fail in strict)
#   7. safe-terminal: no heredocs outside usage/help, no cd && chains
#
# Exit codes:
#   0 — all critical checks passed (warnings OK in default mode)
#   1 — one or more critical checks failed
#   2 — configuration error
#
# Bypass:
#   GENERATION_GATE_BYPASS=1 — skip all checks (logged to .recovery/calibration.jsonl)
#   --no-verify — bypass pre-commit hook

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STRICT="${STRICT:-0}"
NO_SHELLCHECK="${NO_SHELLCHECK:-0}"
BYPASS="${GENERATION_GATE_BYPASS:-0}"

# Colors
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' NC=''
fi

log() { echo -e "${GREEN}[GEN-GATE]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
fail() { echo -e "${RED}[FAIL]${NC} $*" >&2; }

usage() {
    cat <<EOF
generation_gate.sh — Validate bash scripts for generation-time safety

Usage: $(basename "$0") [OPTIONS] [file.sh ...]

Options:
  --strict          Treat warnings as errors
  --no-shellcheck   Skip shellcheck even if installed
  --help            Show this help

Environment:
  STRICT            Same as --strict
  NO_SHELLCHECK     Same as --no-shellcheck
  GENERATION_GATE_BYPASS=1  Skip all checks (logged)

Exit codes:
  0 — all critical checks passed (warnings OK in default mode)
  1 — one or more critical checks failed
  2 — bad configuration
EOF
}

# Parse arguments
TARGET_FILES=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --strict) STRICT=1; shift ;;
        --no-shellcheck) NO_SHELLCHECK=1; shift ;;
        --help) usage; exit 0 ;;
        --no-verify) shift ;; # pre-commit bypass, consumed silently
        -*) fail "Unknown option: $1"; usage >&2; exit 2 ;;
        *) TARGET_FILES+=("$1"); shift ;;
    esac
done

# Bypass
if [[ "$BYPASS" -eq 1 ]]; then
    warn "GENERATION_GATE_BYPASS=1 — skipping all checks"
    echo "$(date '+%Y-%m-%dT%H:%M:%S%z') GENERATION_GATE_BYPASS" >> .recovery/calibration.jsonl 2>/dev/null || true
    exit 0
fi

# Auto-detect target files if none specified
if [[ ${#TARGET_FILES[@]} -eq 0 ]]; then
    if git rev-parse --git-dir &>/dev/null; then
        mapfile -t TARGET_FILES < <(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep '\.sh$' || true)
        if [[ ${#TARGET_FILES[@]} -eq 0 ]]; then
            log "No staged .sh files; checking working tree modifications"
            mapfile -t TARGET_FILES < <(git diff --name-only --diff-filter=ACM 2>/dev/null | grep '\.sh$' || true)
        fi
    fi
    if [[ ${#TARGET_FILES[@]} -eq 0 ]]; then
        log "No target files specified and no .sh files staged/modified. Nothing to check."
        exit 0
    fi
fi

TOTAL_CRITICAL=0
TOTAL_WARNINGS=0

for file in "${TARGET_FILES[@]}"; do
    [[ -f "$file" ]] || continue
    
    log "=== Checking: $file ==="
    CRITICAL=0
    WARNINGS=0
    
    # Check 1: Safety header (critical)
    if ! grep -qE 'set\s+[-+]euo\s+pipefail' "$file"; then
        fail "  Missing 'set -euo pipefail' safety header"
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: Safety header present"
    fi
    
    # Check 2: Environment variable collisions (critical)
    # Look for assignments to reserved env vars (not reads like $LANG)
    local_collisions=$(grep -nE '^\s*(LANG|LC_ALL|PATH|HOME)=' "$file" || true)
    if [[ -n "$local_collisions" ]]; then
        fail "  Environment variable collision (reserved names):"
        echo "$local_collisions" | sed 's/^/    /'
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No env variable collisions"
    fi
    
    # Check 3: Numeric argument validation (warning)
    # Look for shift 2 patterns without validation
    numeric_unvalidated=0
    while IFS= read -r line; do
        lineno=$(echo "$line" | cut -d: -f1)
        # Check if there's a validation pattern within 10 lines before
        if ! sed -n "$((lineno-10)),$((lineno))p" "$file" | grep -qE '\[\[.*\$[0-9].*=~.*[0-9]|\[\[.*-z.*\$[0-9]'; then
            numeric_unvalidated=$((numeric_unvalidated + 1))
        fi
    done < <(grep -nE 'shift\s+2' "$file" || true)
    
    if [[ "$numeric_unvalidated" -gt 0 ]]; then
        warn "  $numeric_unvalidated numeric argument(s) without visible validation"
        WARNINGS=$((WARNINGS + 1))
    else
        log "  PASS: Numeric arguments validated"
    fi
    
    # Check 4: Tool existence checks (warning)
    # Only flag tools that are actually invoked (not in comments/strings)
    missing_checks=0
    for cmd in python3 node npm cargo go javac mvn gradle npx; do
        # Check if tool is invoked as a command (not in comment, string, or variable)
        if grep -vE '^\s*#|^\s*"' "$file" | grep -qE "\b$cmd\b" && ! grep -qE "command\s+-v\s+$cmd\b" "$file"; then
            # Check if there's graceful fallback text nearby
            if ! grep -B3 -A3 "\b$cmd\b" "$file" | grep -qiE "(not installed|not found|skip|missing|warn)"; then
                warn "  Tool '$cmd' used without 'command -v' check or fallback"
                missing_checks=$((missing_checks + 1))
            fi
        fi
    done
    if [[ "$missing_checks" -gt 0 ]]; then
        WARNINGS=$((WARNINGS + missing_checks))
    else
        log "  PASS: Tool existence checked"
    fi
    
    # Check 5: Test co-existence (warning)
    basename_file=$(basename "$file" .sh)
    found_test=0
    for test_path in \
        "$(dirname "$file")/tests/test_${basename_file}.sh" \
        "$(dirname "$file")/tests/test_${basename_file}.py" \
        "$(dirname "$file")/../tests/test_${basename_file}.sh" \
        "$(dirname "$file")/../tests/test_${basename_file}.py" \
        "tests/test_${basename_file}.sh" \
        "tests/test_${basename_file}.py"
    do
        if [[ -f "$test_path" ]]; then
            found_test=1
            break
        fi
    done
    
    if [[ "$found_test" -eq 0 ]]; then
        warn "  No matching test file found (test_${basename_file}.sh or .py)"
        WARNINGS=$((WARNINGS + 1))
    else
        log "  PASS: Test file exists"
    fi
    
    # Check 6: shellcheck (warning)
    if [[ "$NO_SHELLCHECK" -eq 0 ]] && command -v shellcheck &>/dev/null; then
        sc_output=$(shellcheck "$file" 2>/dev/null || true)
        sc_issues=$(echo "$sc_output" | grep -c '^\s*\^' || echo 0)
        if [[ "$sc_issues" -gt 0 ]]; then
            warn "  shellcheck found $sc_issues issue(s):"
            echo "$sc_output" | head -20 | sed 's/^/    /'
            WARNINGS=$((WARNINGS + sc_issues))
        else
            log "  PASS: shellcheck clean"
        fi
    elif [[ "$NO_SHELLCHECK" -eq 0 ]]; then
        warn "  shellcheck not installed; skipping"
    fi
    
    # Check 7: safe-terminal compliance
    # No heredocs outside usage/help functions (critical)
    heredocs_outside_usage=0
    while IFS= read -r line; do
        lineno=$(echo "$line" | cut -d: -f1)
        start=$(( lineno - 5 ))
        [[ "$start" -lt 1 ]] && start=1
        end=$(( lineno + 5 ))
        if ! sed -n "${start},${end}p" "$file" | grep -qE 'usage\(\)|help\(\)|--help'; then
            heredocs_outside_usage=$((heredocs_outside_usage + 1))
        fi
    done < <(grep -nE '<<[A-Z]' "$file" || true)
    
    if [[ "$heredocs_outside_usage" -gt 0 ]]; then
        fail "  safe-terminal: heredoc outside usage/help function (use write_to_file):"
        grep -nE '<<[A-Z]' "$file" | sed 's/^/    /'
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No unsafe heredocs"
    fi
    
    # No cd && chains except standard SCRIPT_DIR pattern (critical)
    # Exclude: comments, string literals in echo/fail/warn, SCRIPT_DIR pattern
    cd_chains=$(grep -nE 'cd\s+.*&&' "$file" | grep -vE '^[0-9]+:\s*#|^[0-9]+:\s*(echo|fail|warn|log)\s+' | grep -v 'SCRIPT_DIR=' || true)
    if [[ -n "$cd_chains" ]]; then
        fail "  safe-terminal: 'cd ... &&' chain detected (use Cwd param or SCRIPT_DIR pattern):"
        echo "$cd_chains" | head -3 | sed 's/^/    /'
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No cd && chains"
    fi
    
    # Summary for this file
    if [[ "$CRITICAL" -gt 0 ]]; then
        fail "  FAILED: $CRITICAL critical, $WARNINGS warning(s)"
        TOTAL_CRITICAL=$((TOTAL_CRITICAL + CRITICAL))
    elif [[ "$WARNINGS" -gt 0 ]]; then
        warn "  PASSED with $WARNINGS warning(s)"
    else
        log "  PASSED: clean"
    fi
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + WARNINGS))
    echo ""
done

if [[ "$TOTAL_CRITICAL" -gt 0 ]]; then
    fail "=== GENERATION GATE FAILED: $TOTAL_CRITICAL critical issue(s) ==="
    fail "Fix the critical issues above and re-run."
    fail "To bypass: GENERATION_GATE_BYPASS=1 <command>"
    exit 1
elif [[ "$TOTAL_WARNINGS" -gt 0 && "$STRICT" -eq 1 ]]; then
    fail "=== GENERATION GATE FAILED: $TOTAL_WARNINGS warning(s) in strict mode ==="
    fail "Fix warnings or run without --strict"
    fail "To bypass: GENERATION_GATE_BYPASS=1 <command>"
    exit 1
else
    log "=== GENERATION GATE PASSED ==="
    if [[ "$TOTAL_WARNINGS" -gt 0 ]]; then
        warn "$TOTAL_WARNINGS warning(s) present (not blocking in default mode)"
    fi
    exit 0
fi
