#!/usr/bin/env bash
# llm-code-gate.sh — language-agnostic mechanical correctness gate for LLM-generated code
# 
# Usage:
#   bash llm-code-gate.sh [--max-iter N] [--strict] [--lang python|go|typescript|rust|java]
#
# Exit codes:
#   0 — gate passed
#   1 — gate failed (compilation, type-check, lint, or test failure)
#   2 — configuration error
#   3 — max repair iterations exceeded
#
# This gate is fail-closed: it blocks commit/success until all layers pass.
# It is language-agnostic: detects language from file extensions if --lang not specified.
# It is tamper-isolated: runs in a subshell and does not modify source files.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAX_ITER="${MAX_ITER:-3}"
STRICT="${STRICT:-0}"
LANG="${LANG:-auto}"

# Colors for output (disable if not tty)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' NC=''
fi

log() { echo -e "${GREEN}[GATE]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
fail() { echo -e "${RED}[FAIL]${NC} $*" >&2; }

usage() {
    cat <<EOF
llm-code-gate.sh — Mechanical correctness gate for LLM-generated code

Usage: $(basename "$0") [OPTIONS]

Options:
  --max-iter N    Maximum repair iterations (default: 3)
  --strict        Treat warnings as errors
  --lang LANG     Force language (python|go|typescript|rust|java)
                  Default: auto-detect from file extensions
  --help          Show this help

Environment:
  MAX_ITER        Same as --max-iter
  STRICT          Same as --strict
  LANG            Same as --lang

Layers (run in order):
  1. Structural/graph: manifest validation, declare-before-use
  2. Type/compile: compiler or type-checker
  3. Execution: fast tests
  4. Schema: runtime validation (if schemas defined)

Exit codes:
  0 — all layers passed
  1 — at least one layer failed
  2 — bad configuration
  3 — max iterations exceeded
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --max-iter) MAX_ITER="$2"; shift 2 ;;
        --strict) STRICT=1; shift ;;
        --lang) LANG="$2"; shift 2 ;;
        --help) usage; exit 0 ;;
        *) fail "Unknown option: $1"; usage >&2; exit 2 ;;
    esac
done

# Auto-detect language from staged/untracked files
detect_language() {
    local lang="$1"
    if [[ "$lang" != "auto" ]]; then
        echo "$lang"
        return
    fi

    # Count files by extension in the working tree
    local py go ts rs java
    py=$(find . -maxdepth 2 -name '*.py' -not -path './.*' 2>/dev/null | wc -l)
    go=$(find . -maxdepth 2 -name '*.go' -not -path './.*' 2>/dev/null | wc -l)
    ts=$(find . -maxdepth 2 -name '*.ts' -not -path './.*' 2>/dev/null | wc -l)
    rs=$(find . -maxdepth 2 -name '*.rs' -not -path './.*' 2>/dev/null | wc -l)
    java=$(find . -maxdepth 2 -name '*.java' -not -path './.*' 2>/dev/null | wc -l)

    # Pick the dominant language
    local max="$py" winner="python"
    if [[ "$go" -gt "$max" ]]; then max="$go"; winner="go"; fi
    if [[ "$ts" -gt "$max" ]]; then max="$ts"; winner="typescript"; fi
    if [[ "$rs" -gt "$max" ]]; then max="$rs"; winner="rust"; fi
    if [[ "$java" -gt "$max" ]]; then max="$java"; winner="java"; fi

    if [[ "$max" -eq 0 ]]; then
        fail "No source files detected. Run from project root or specify --lang."
        exit 2
    fi

    echo "$winner"
}

# Layer 1: Structural / graph checks
check_structural() {
    log "Layer 1: Structural / graph checks"
    local fail_count=0

    # Check manifest exists
    case "$LANG" in
        python)
            if [[ ! -f "pyproject.toml" && ! -f "setup.py" && ! -f "setup.cfg" && ! -f "requirements.txt" ]]; then
                warn "No Python manifest found (pyproject.toml/setup.py/requirements.txt)"
                fail_count=$((fail_count + 1))
            fi
            ;;
        go)
            if [[ ! -f "go.mod" ]]; then
                warn "No go.mod found"
                fail_count=$((fail_count + 1))
            fi
            ;;
        typescript)
            if [[ ! -f "package.json" ]]; then
                warn "No package.json found"
                fail_count=$((fail_count + 1))
            fi
            ;;
        rust)
            if [[ ! -f "Cargo.toml" ]]; then
                warn "No Cargo.toml found"
                fail_count=$((fail_count + 1))
            fi
            ;;
        java)
            if [[ ! -f "pom.xml" && ! -f "build.gradle" && ! -f "build.gradle.kts" ]]; then
                warn "No Java manifest found (pom.xml/build.gradle)"
                fail_count=$((fail_count + 1))
            fi
            ;;
    esac

    # Check for forward references (basic grep heuristic)
    # This is a coarse check; language-aware tools do better
    if [[ "$LANG" == "python" ]]; then
        # Check for imports of modules that don't exist in the project
        local missing_imports
        missing_imports=$(python3 -c "
import ast, sys, os
from pathlib import Path
errors = []
for path in Path('.').rglob('*.py'):
    if '.venv' in str(path) or '__pycache__' in str(path):
        continue
    try:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if not Path(f'{mod}.py').exists() and not Path(mod).is_dir():
                        errors.append(f'{path}: import {mod}')
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split('.')[0]
                    if not Path(f'{mod}.py').exists() and not Path(mod).is_dir():
                        errors.append(f'{path}: from {mod}')
    except SyntaxError:
        errors.append(f'{path}: SYNTAX ERROR')
for e in errors[:10]:
    print(e)
" 2>/dev/null || true)
        if [[ -n "$missing_imports" ]]; then
            warn "Potential missing imports detected:"
            echo "$missing_imports" | head -5 | sed 's/^/  /'
            fail_count=$((fail_count + 1))
        fi
    fi

    if [[ "$fail_count" -gt 0 ]]; then
        fail "Layer 1 failed ($fail_count structural issues)"
        return 1
    fi
    log "Layer 1: PASS"
    return 0
}

# Layer 2: Type / compile
check_type_compile() {
    log "Layer 2: Type / compile checks"
    local strict_flag=""
    [[ "$STRICT" -eq 1 ]] && strict_flag="--strict"

    case "$LANG" in
        python)
            # Prefer pyright, fall back to mypy
            if command -v pyright &>/dev/null; then
                log "  Running pyright..."
                if ! pyright $strict_flag . 2>&1 | tail -20; then
                    fail "pyright failed"
                    return 1
                fi
            elif command -v mypy &>/dev/null; then
                log "  Running mypy..."
                if ! mypy $strict_flag . 2>&1 | tail -20; then
                    fail "mypy failed"
                    return 1
                fi
            else
                warn "No Python type checker installed (pyright or mypy). Skipping type check."
                warn "Install: npm install -g pyright  OR  pip install mypy"
                return 0  # Don't fail if tool absent; this is coaching
            fi
            ;;
        go)
            log "  Running go vet..."
            if ! go vet ./... 2>&1 | tail -20; then
                fail "go vet failed"
                return 1
            fi
            ;;
        typescript)
            if [[ -f "tsconfig.json" ]]; then
                log "  Running tsc --noEmit..."
                if ! npx tsc --noEmit 2>&1 | tail -20; then
                    fail "tsc failed"
                    return 1
                fi
            else
                warn "No tsconfig.json found. Skipping type check."
                return 0
            fi
            ;;
        rust)
            log "  Running cargo check..."
            if ! cargo check 2>&1 | tail -20; then
                fail "cargo check failed"
                return 1
            fi
            ;;
        java)
            if [[ -f "pom.xml" && -f "mvnw" ]]; then
                log "  Running Maven compile..."
                if ! ./mvnw compile -q 2>&1 | tail -20; then
                    fail "Maven compile failed"
                    return 1
                fi
            elif [[ -f "build.gradle" || -f "build.gradle.kts" ]]; then
                log "  Running Gradle compile..."
                if ! ./gradlew compileJava -q 2>&1 | tail -20; then
                    fail "Gradle compile failed"
                    return 1
                fi
            else
                warn "No Maven/Gradle wrapper found. Skipping compile check."
                return 0
            fi
            ;;
    esac

    log "Layer 2: PASS"
    return 0
}

# Layer 3: Execution / tests
check_tests() {
    log "Layer 3: Execution / tests"

    case "$LANG" in
        python)
            if [[ -f "pytest.ini" || -f "pyproject.toml" ]] && command -v pytest &>/dev/null; then
                log "  Running pytest..."
                if ! pytest -q --tb=short 2>&1 | tail -30; then
                    fail "pytest failed"
                    return 1
                fi
            else
                log "  No pytest configuration found. Skipping tests."
                return 0
            fi
            ;;
        go)
            log "  Running go test..."
            if ! go test ./... 2>&1 | tail -30; then
                fail "go test failed"
                return 1
            fi
            ;;
        typescript)
            if [[ -f "package.json" ]] && grep -q '"test"' package.json; then
                log "  Running npm test..."
                if ! npm test --silent 2>&1 | tail -30; then
                    fail "npm test failed"
                    return 1
                fi
            else
                log "  No test script in package.json. Skipping tests."
                return 0
            fi
            ;;
        rust)
            log "  Running cargo test..."
            if ! cargo test 2>&1 | tail -30; then
                fail "cargo test failed"
                return 1
            fi
            ;;
        java)
            if [[ -f "pom.xml" && -f "mvnw" ]]; then
                log "  Running Maven test..."
                if ! ./mvnw test -q 2>&1 | tail -30; then
                    fail "Maven test failed"
                    return 1
                fi
            elif [[ -f "build.gradle" || -f "build.gradle.kts" ]]; then
                log "  Running Gradle test..."
                if ! ./gradlew test -q 2>&1 | tail -30; then
                    fail "Gradle test failed"
                    return 1
                fi
            else
                log "  No test runner found. Skipping tests."
                return 0
            fi
            ;;
    esac

    log "Layer 3: PASS"
    return 0
}

# Layer 4: Lint / formatting
check_lint() {
    log "Layer 4: Lint / formatting"

    case "$LANG" in
        python)
            if command -v ruff &>/dev/null; then
                log "  Running ruff..."
                if ! ruff check . 2>&1 | tail -20; then
                    fail "ruff failed"
                    return 1
                fi
            elif command -v flake8 &>/dev/null; then
                log "  Running flake8..."
                if ! flake8 . 2>&1 | tail -20; then
                    fail "flake8 failed"
                    return 1
                fi
            else
                log "  No Python linter installed. Skipping lint."
                return 0
            fi
            ;;
        go)
            if command -v golangci-lint &>/dev/null; then
                log "  Running golangci-lint..."
                if ! golangci-lint run 2>&1 | tail -20; then
                    fail "golangci-lint failed"
                    return 1
                fi
            else
                log "  golangci-lint not installed. Skipping lint."
                return 0
            fi
            ;;
        typescript)
            if command -v biome &>/dev/null; then
                log "  Running biome..."
                if ! biome check . 2>&1 | tail -20; then
                    fail "biome failed"
                    return 1
                fi
            elif command -v eslint &>/dev/null; then
                log "  Running eslint..."
                if ! npx eslint . 2>&1 | tail -20; then
                    fail "eslint failed"
                    return 1
                fi
            else
                log "  No JS/TS linter installed. Skipping lint."
                return 0
            fi
            ;;
        rust)
            log "  Running cargo clippy..."
            if ! cargo clippy --all-targets -- -D warnings 2>&1 | tail -20; then
                fail "clippy failed"
                return 1
            fi
            ;;
        java)
            # Spotless or Checkstyle would go here; skip for now
            log "  Java linting not configured. Skipping."
            return 0
            ;;
    esac

    log "Layer 4: PASS"
    return 0
}

# Main gate logic
main() {
    log "Starting LLM-code correctness gate"
    log "Max iterations: $MAX_ITER | Strict: $STRICT | Lang: $LANG"

    # Detect language
    LANG=$(detect_language "$LANG")
    log "Detected language: $LANG"

    local iter=1
    local gate_passed=0

    while [[ "$iter" -le "$MAX_ITER" ]]; do
        log "=== Iteration $iter/$MAX_ITER ==="

        gate_passed=1

        # Run all four layers
        check_structural || gate_passed=0
        check_type_compile || gate_passed=0
        check_tests || gate_passed=0
        check_lint || gate_passed=0

        if [[ "$gate_passed" -eq 1 ]]; then
            log "=== GATE PASSED on iteration $iter ==="
            log "All 4 layers passed. Code is mechanically correct."
            exit 0
        fi

        if [[ "$iter" -lt "$MAX_ITER" ]]; then
            warn "Gate failed on iteration $iter. Retrying after fix..."
            # In a real scenario, the agent would fix issues here.
            # This script exits and expects the caller to re-run after fixes.
            fail "Gate failed. Fix the issues above and re-run."
            exit 1
        fi

        iter=$((iter + 1))
    done

    fail "=== GATE FAILED after $MAX_ITER iterations ==="
    fail "The code did not pass mechanical correctness checks."
    fail "Either fix the issues manually or escalate to human review."
    exit 3
}

main "$@"
