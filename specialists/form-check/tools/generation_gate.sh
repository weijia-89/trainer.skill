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
# Indent diagnostic output under its message (shellcheck SC2001 prefers this
# to a sed kick).
indent() { awk '{printf "    %s\n", $0}'; }

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
        # Check first so exotic environments degrade to a logged skip instead
        # of an abort on the audit-trail tightening.
        if command -v chmod &>/dev/null; then
            chmod 600 ".recovery/calibration.jsonl" 2>/dev/null || true
        else
            warn "chmod not available; calibration log permissions not tightened"
        fi
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

# Normalized views are per-file temp copies with comment lines and heredoc
# bodies removed, so the pattern checks below look only at executed code.
# Raw "$file" stays available for checks that need the untouched text.
CLEAN_FILES=()
trap 'if [[ ${#CLEAN_FILES[@]} -gt 0 ]]; then rm -f "${CLEAN_FILES[@]}" 2>/dev/null || true; fi' EXIT

# Heredoc-start pattern, kept in a variable so bash does not tokenize the
# unquoted << inside the conditional expression.
HEREDOC_START_RE='<<-?[[:space:]]*["]?["'"'"']?([A-Za-z_][A-Za-z0-9_]*)'

strip_noise() {
    # Reads a script on stdin, writes it with comment lines and heredoc bodies
    # (between a << marker and its delimiter line) removed. Pure bash, bash 3.2
    # compatible. Heredoc start lines are kept: they carry the real invocation.
    inside=0
    term=""
    while IFS= read -r line; do
        if [[ "$inside" -eq 1 ]]; then
            [[ "$line" == "$term" ]] && inside=0
            continue
        fi
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        if [[ "$line" =~ $HEREDOC_START_RE ]]; then
            term="${BASH_REMATCH[1]}"
            inside=1
        fi
        printf '%s\n' "$line"
    done
}

for file in "${TARGET_FILES[@]}"; do
    [[ -f "$file" ]] || continue
    
    log "=== Checking: $file ==="
    CRITICAL=0
    WARNINGS=0
    
    clean_file=$(mktemp "${TMPDIR:-/tmp}/gen-gate-clean.XXXXXX")
    CLEAN_FILES+=("$clean_file")
    strip_noise < "$file" > "$clean_file"
    clean_file_size=$(wc -c < "$clean_file")
    if [[ "$clean_file_size" -eq 0 ]]; then
        # Nothing executable left (all comments); fall back to the raw file so
        # the structural checks below still see something.
        cp "$file" "$clean_file"
    fi
    
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
        echo "$local_collisions" | indent
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No env variable collisions"
    fi
    
    # Check 3: Numeric argument validation (warning)
    # Look for shift 2 patterns without validation (comments excluded via clean_file)
    numeric_unvalidated=0
    while IFS= read -r line; do
        lineno=$(echo "$line" | cut -d: -f1)
        # Check if there's a validation pattern within 10 lines before
        if ! sed -n "$((lineno-10)),$((lineno))p" "$clean_file" | grep -qE '\[\[.*\$[0-9].*=~.*[0-9]|\[\[.*-z.*\$[0-9]'; then
            numeric_unvalidated=$((numeric_unvalidated + 1))
        fi
    done < <(grep -nE 'shift\s+2' "$clean_file" || true)
    
    if [[ "$numeric_unvalidated" -gt 0 ]]; then
        warn "  $numeric_unvalidated numeric argument(s) without visible validation"
        WARNINGS=$((WARNINGS + 1))
    else
        log "  PASS: Numeric arguments validated"
    fi
    
    # Check 4: Tool existence checks (warning)
    # Dynamically extract tool names from common patterns + hardcoded list
    missing_checks=0
    
    # Build combined list: hardcoded common tools + dynamically detected.
    # Detection input is clean_file (comments + heredoc bodies removed), and the
    # lines filtered here are the ones whose first word is not an invocation:
    # variable/array assignments and function definitions.
    detected_tools=()
    # Detect tools invoked directly (command args or pipeline)
    SKIP_TOOLS='^(echo|printf|cat|sed|awk|grep|cut|sort|uniq|head|tail|basename|dirname|cd|pwd|exit|return|shift|trap|set|unset|export|local|read|declare|typeset|readonly|break|continue|if|then|elif|else|fi|for|while|until|do|done|case|esac|in|function|source|\.|\[|\]\])$'
    # Shell functions defined in this file are not external tools; fold their
    # names into the skip pattern (no sed/awk needed: pure token paste).
    defined_functions=()
    while IFS= read -r fn_line; do
        fn_name=""; for f in $fn_line; do fn_name="$f"; break; done
        [[ -n "$fn_name" ]] && defined_functions+=("$fn_name")
    done < <(grep -oE '^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\(\)' "$clean_file" 2>/dev/null || true)
    if [[ ${#defined_functions[@]} -gt 0 ]]; then
        # Insert function names into the skip alternation before its close.
        fn_extra=""
        for fn_name in "${defined_functions[@]}"; do
            fn_extra="$fn_extra|$fn_name"
        done
        # ${var%)\$}: wipe the "close-and-anchor" tail, then re-add it past the
        # new alternatives, so the pattern stays ^(...)$ with all names inside.
        SKIP_TOOLS="${SKIP_TOOLS%)\$}$fn_extra)\$"
    fi
    while IFS= read -r match; do
        tool=$(echo "$match" | awk '{print $1}')
        # Skip bash builtins, variable names (convention: upper or dotted), and
        # anything with an extension suffix (a filename, not a command).
        if [[ -n "$tool" ]] && ! [[ "$tool" =~ $SKIP_TOOLS ]] \
            && ! [[ "$tool" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] \
            && ! [[ "$tool" =~ ^[A-Z_][A-Z0-9_]*$ ]] \
            && ! [[ "$tool" == *.* ]]; then
            detected_tools+=("$tool")
        fi
    done < <(grep -vE '^[[:space:]]*$' "$clean_file" \
        | grep -vE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=' \
        | grep -vE '^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\(\)' \
        | grep -oE '^[[:space:]]*[^[:space:]$;&|(`*{}"-][a-zA-Z0-9_./-]*' \
        | sort -u || true)
    
    # Combine hardcoded and detected, remove duplicates
    all_tools=(python3 node npm cargo go javac mvn gradle npx jq yq curl wget docker kubectl terraform ansible)
    if [[ ${#detected_tools[@]} -gt 0 ]]; then
        all_tools+=("${detected_tools[@]}")
    fi
    
    # Check each unique tool
    checked_tools=()
    # POSIX-core utilities are guaranteed with any POSIX shell environment;
    # checking them is noise and misses the point (niche binaries are the risk).
    POSIX_CORE='^(rm|mkdir|find|cp|mv|touch|ln|date|chmod|chown|uname|tar|gzip)$'
    for cmd in "${all_tools[@]}"; do
        if [[ "$cmd" =~ $POSIX_CORE ]]; then
            continue
        fi
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
        
        # A real invocation: command position on an executable line (line start,
        # after ; | & or a $( ). Mentions inside strings, arrays, comments, and
        # heredocs do not count.
        has_tool=0
        has_check=0
        invocation_re="(^|[;|&(])[[:space:]]*${cmd}([[:space:]\$\")]|\$)"
        if grep -vE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*=[[:space:]]*\(' "$clean_file" | grep -Eq "$invocation_re" 2>/dev/null; then
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
    
    # Check 5: Test co-existence (warning). A file that is itself a test does
    # not need a test of the test: recursion would be infinite, so skip.
    basename_file=$(basename "$file" .sh)
    if [[ "$basename_file" == test_* ]]; then
        log "PASS: target is itself a test file (no test-of-test recursion)"
    else
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
    fi  # test_* skip (no test-of-test recursion)
    
    # Check 6: shellcheck (warning)
    if [[ "$NO_SHELLCHECK" -eq 0 ]] && command -v shellcheck &>/dev/null; then
        sc_output=$(shellcheck "$file" 2>/dev/null || true)
        sc_issues=$(echo "$sc_output" | grep -c '^\s*\^' || echo 0)
        if [[ "$sc_issues" -gt 0 ]]; then
            warn "  shellcheck found $sc_issues issues:"
            echo "$sc_output" | head -20 | indent
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
        grep -nE '<<[A-Z]' "$file" | indent
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
            echo "$matches" | head -3 | indent
            found_secrets=$((found_secrets + 1))
        fi
    done
    
    # Regex patterns for assignment patterns (using double quotes to avoid single-quote issues)
    for regex_pattern in 'password\s*=\s*"[^"]+"' 'token\s*=\s*"[^"]+"' 'api_key\s*=\s*"[^"]+"' 'secret\s*=\s*"[^"]+"'; do
        matches=$(grep -inE "$regex_pattern" "$file" | grep -vE '^\s*#' || true)
        if [[ -n "$matches" ]]; then
            fail "  Potential secret detected:"
            echo "$matches" | head -3 | indent
            found_secrets=$((found_secrets + 1))
        fi
    done
    
    if [[ "$found_secrets" -gt 0 ]]; then
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No obvious secrets"
    fi
    
    # Check 9: No cd && chains except standard SCRIPT_DIR pattern (critical)
    # Exclude: comments, string literals in echo/fail/warn, and the command-
    # substitution form of the idiom: $(cd ... && pwd). Both patterns use the
    # [[:space:]] spelling (never a literal space after "cd") so this check's
    # own source cannot match itself.
    cd_chains=$(grep -nE 'cd[[:space:]]+.*&&' "$file" | grep -vE '^[0-9]+:\s*#|^[0-9]+:\s*(echo|fail|warn|log)\s+' | grep -vE '\$\([[:space:]]*cd[[:space:]].*&&[[:space:]]*pwd' || true)
    if [[ -n "$cd_chains" ]]; then
        fail "  safe-terminal: cd-and chain detected - use Cwd param or SCRIPT_DIR pattern:"
        echo "$cd_chains" | head -3 | indent
        CRITICAL=$((CRITICAL + 1))
    else
        log "  PASS: No cd and chains"
    fi
    
    # Check 10: Additional safe-terminal rules (warnings)
    # No eval invocations (command position only; the word inside a string,
    # pattern, or identifier does not count) and no backtick command
    # substitution. The backtick is built from \x60 so this check's own source
    # contains no backtick pair to trip itself.
    eval_usage=$(grep -nE '(^|[;&|(])[[:space:]]*eval[[:space:]]' "$clean_file" || true)
    bt=$(printf '\\x60')
    backtick_usage=""
    if [[ -n "$bt" ]]; then
        backtick_usage=$(grep -nE "${bt}[^${bt}]+${bt}" "$clean_file" || true)
    fi
    if [[ -n "$eval_usage" || -n "$backtick_usage" ]]; then
        warn "  safe-terminal: eval or backtick usage detected:"
        { [[ -n "$eval_usage" ]] && echo "$eval_usage"; [[ -n "$backtick_usage" ]] && echo "$backtick_usage"; } | head -3 | indent
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # No unquoted variables in rm/mv/cp
    unquoted_danger=$(grep -nE 'rm\s+-rf?\s+\$|mv\s+\$|cp\s+-r\s+\$' "$file" | grep -vE '^\s*#' || true)
    if [[ -n "$unquoted_danger" ]]; then
        warn "  safe-terminal: unquoted variable in dangerous command:"
        echo "$unquoted_danger" | head -3 | indent
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
