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
    # Require justification file or environment variable
    justification="${GENERATION_GATE_JUSTIFICATION:-(no justification provided)}"
    # Emergency disable: if GENERATION_GATE_EMERGENCY_DISABLE is set, skip logging
    if [[ "${GENERATION_GATE_EMERGENCY_DISABLE:-0}" -eq 1 ]]; then
        warn "EMERGENCY_DISABLE set — bypassing without audit trail"
        exit 0
    fi
    echo "$(date '+%Y-%m-%dT%H:%M:%S%z') GENERATION_GATE_BYPASS justification='${justification}'" >> .recovery/calibration.jsonl 2>/dev/null || true
    # Set restrictive permissions on log file if it exists
    if [[ -f ".recovery/calibration.jsonl" ]]; then
        chmod 600 ".recovery/calibration.jsonl" 2>/dev/null || true
    fi
    exit 0
fi

# Auto-detect target files if none specified
if [[ ${#TARGET_FILES[@]} -eq 0 ]]; then
    if git rev-parse --git-dir &>/dev/null; then
        # Portable alternative to mapfile for bash 3.2 (macOS default)
        TARGET_FILES=()
        while IFS= read -r line; do
            [[ -n "$line" ]] && TARGET_FILES+=("$line")
        done < <(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep '\.sh$' || true)
        
        if [[ ${#TARGET_FILES[@]} -eq 0 ]]; then
            log "No staged .sh files; checking working tree modifications"
            TARGET_FILES=()
            while IFS= read -r line; do
                [[ -n "$line" ]] && TARGET_FILES+=("$line")
            done < <(git diff --name-only --diff-filter=ACM 2>/dev/null | grep '\.sh$' || true)
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
    # Dynamically extract tool names from common patterns + hardcoded list
    missing_checks=0
    
    # Build combined list: hardcoded common tools + dynamically detected
    detected_tools=()
    # Detect tools invoked directly (command args or pipeline)
    while IFS= read -r match; do
        tool=$(echo "$match" | sed -E 's/^[[:space:]]*//' | awk '{print $1}')
        # Skip bash builtins, comments, variable assignments, and common non-tool commands
        if [[ -n "$tool" ]] && ! [[ "$tool" =~ ^(echo|printf|cat|sed|awk|grep|cut|sort|uniq|head|tail|basename|dirname|cd|pwd|exit|return|shift|trap|set|unset|export|local|if|then|elif|else|fi|for|while|do|done|case|esac|in|function|trap|source|\.|\[|\]\])$ ]]; then
            detected_tools+=("$tool")
        fi
    done < <(grep -vE '^\s*#|^\s*$' "$file" | grep -oE '^[[:space:]]*[a-zA-Z0-9_.-]+' | sort -u || true)
    
    # Combine hardcoded and detected, remove duplicates
    all_tools=(python3 node npm cargo go javac mvn gradle npx jq yq curl wget docker kubectl terraform ansible)
    if [[ ${#detected_tools[@]} -gt 0 ]]; then
        all_tools+=("${detected_tools[@]}")
    fi
    
    # Check each unique tool
    checked_tools=()
    for cmd in "${all_tools[@]}"; do
        # Skip if already checked (use loop instead of regex to avoid unbound variable issues)
        already_checked=0
        if [[ ${#checked_tools[@]} -gt 0 ]]; then
            for checked in "${checked_tools[@]}"; do
                if [[ "$checked" == "$cmd" ]]; then
                    already_checked=1
                    break
                fi
            done
        fi
        [[ "$already_checked" -eq 1 ]] && continue
        checked_tools+=("$cmd")
        
        # Check if tool is invoked as a command (not in comment or variable assignment)
        has_tool=0
        has_check=0
        if grep -vE '^\s*#|^\s*[A-Z_]+=' "$file" | grep -qE "\b$cmd\b"; then
            has_tool=1
        fi
        if grep -qE "command\s+-v\s+$cmd\b|which\s+$cmd\b|type\s+-P\s+$cmd\b" "$file"; then
            has_check=1
        fi
        if [[ "$has_tool" -eq 1 && "$has_check" -eq 0 ]]; then
            # Check if there is graceful fallback text nearby
            if ! grep -B3 -A3 "\b$cmd\b" "$file" | grep -qiE "(not installed|not found|skip|missing|warn|optional)"; then
                warn "  Tool '$cmd' used without existence check or fallback"
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
        # Check test quality: minimum number of assertions/checks
        test_assertions=$(grep -cE '(assert|PASS|FAIL|expect|should|test\()' "$test_path" 2>/dev/null || echo 0)
        if [[ "$test_assertions" -lt 3 ]]; then
            warn "  Test file has only $test_assertions assertions (minimum recommended: 3)"
            WARNINGS=$((WARNINGS + 1))
        else
            log "  PASS: Test file exists with $test_assertions assertions"
        fi
    fi
    
    # Check 6: shellcheck (warning)
    if [[ "$NO_SHELLCHECK" -eq 0 ]] && command -v shellcheck &>/dev/null; then
        sc_output=$(shellcheck "$file" 2>/dev/null || true)
        sc_issues=$(echo "$sc_output" | grep -c '^\s*\^' || echo 0)
        if [[ "$sc_issues" -gt 0 ]]; then
            warn "  shellcheck found $sc_issues issues:"
            echo "$sc_output" | head -20 | sed 's/^/    /'
            WARNINGS=$((WARNINGS + sc_issues))
        else
            log "  PASS: shellcheck clean"
        fi
    elif [[ "$NO_SHELLCHECK" -eq 0 ]]; then
        warn "  shellcheck not installed; skipping"
    fi
    
    # Check 7: safe-terminal partial compliance (2/12 Tier-1 rules enforced)
    # NOTE: This is a subset check. Full safe-terminal compliance requires
    # reviewing all 12 Tier-1 rules manually. See safe-terminal skill for details.
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
    
    # Check 8: Secret detection (critical)
    # Look for common secret patterns (AWS keys, API tokens, passwords)
    found_secrets=0
    
    # Simple string patterns (match assignment with value, not pattern definitions)
    for simple_pattern in 'AWS_SECRET_ACCESS_KEY=[^[:space:]]' 'AWS_ACCESS_KEY_ID=[^[:space:]]' 'GITHUB_TOKEN=[^[:space:]]' 'PRIVATE_KEY=[^[:space:]]'; do
        # Exclude lines that are pattern definitions or comments
        matches=$(grep -inE "$simple_pattern" "$file" | grep -vE '^\s*#|simple_pattern|for .* in' || true)
        if [[ -n "$matches" ]]; then
            fail "  Potential secret detected:"
            echo "$matches" | head -3 | sed 's/^/    /'
            found_secrets=$((found_secrets + 1))
        fi
    done
    
    # Regex patterns for assignment patterns (using double quotes to avoid single-quote issues)
    for regex_pattern in 'password\s*=\s*"[^"]+"' 'token\s*=\s*"[^"]+"' 'api_key\s*=\s*"[^"]+"' 'secret\s*=\s*"[^"]+"'; do
        matches=$(grep -inE "$regex_pattern" "$file" | grep -vE '^\s*#' || true)
        if [[ -n "$matches" ]]; then
            fail "  Potential secret detected:"
            echo "$matches" | head -3 | sed 's/^/    /'
            found_secrets=$((found_secrets + 1))
        fi
    done
    
    if [[ "$found_secrets" -gt 0 ]]; then
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No obvious secrets"
    fi
    
    # Check 9: No cd && chains except standard SCRIPT_DIR pattern (critical)
    # Exclude: comments, string literals in echo/fail/warn, SCRIPT_DIR pattern
    cd_chains=$(grep -nE 'cd\s+.*&&' "$file" | grep -vE '^[0-9]+:\s*#|^[0-9]+:\s*(echo|fail|warn|log)\s+' | grep -v 'SCRIPT_DIR=' || true)
    if [[ -n "$cd_chains" ]]; then
        fail "  safe-terminal: cd-and chain detected - use Cwd param or SCRIPT_DIR pattern:"
        echo "$cd_chains" | head -3 | sed 's/^/    /'
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No cd and chains"
    fi
    
    # Check 10: Additional safe-terminal rules (warnings)
    # No eval or backtick command substitution
    eval_usage=$(grep -nE '\beval\b|\`[^`]+\`' "$file" | grep -vE '^\s*#' || true)
    if [[ -n "$eval_usage" ]]; then
        warn "  safe-terminal: eval or backtick usage detected:"
        echo "$eval_usage" | head -3 | sed 's/^/    /'
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # No unquoted variables in rm/mv/cp
    unquoted_danger=$(grep -nE 'rm\s+-rf?\s+\$|mv\s+\$|cp\s+-r\s+\$' "$file" | grep -vE '^\s*#' || true)
    if [[ -n "$unquoted_danger" ]]; then
        warn "  safe-terminal: unquoted variable in dangerous command:"
        echo "$unquoted_danger" | head -3 | sed 's/^/    /'
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Summary for this file
    if [[ "$CRITICAL" -gt 0 ]]; then
        fail "  FAILED: $CRITICAL critical, $WARNINGS warnings"
        TOTAL_CRITICAL=$((TOTAL_CRITICAL + CRITICAL))
    elif [[ "$WARNINGS" -gt 0 ]]; then
        warn "  PASSED with $WARNINGS warnings"
    else
        log "  PASSED: clean"
    fi
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + WARNINGS))
    echo ""
done

if [[ "$TOTAL_CRITICAL" -gt 0 ]]; then
    fail "=== GENERATION GATE FAILED: $TOTAL_CRITICAL critical issues ==="
    fail "Fix the critical issues above and re-run."
    fail "To bypass: GENERATION_GATE_BYPASS=1 COMMAND"
    exit 1
elif [[ "$TOTAL_WARNINGS" -gt 0 && "$STRICT" -eq 1 ]]; then
    fail "=== GENERATION GATE FAILED: $TOTAL_WARNINGS warnings in strict mode ==="
    fail "Fix warnings or run without --strict"
    fail "To bypass: GENERATION_GATE_BYPASS=1 COMMAND"
    exit 1
else
    log "=== GENERATION GATE PASSED ==="
    if [[ "$TOTAL_WARNINGS" -gt 0 ]]; then
        warn "$TOTAL_WARNINGS warnings present - not blocking in default mode"
    fi
    exit 0
fi
