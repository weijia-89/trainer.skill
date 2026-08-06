#!/usr/bin/env bash
# test-pr-format.sh — Validate PR body and review comment against templates.
# Usage: bash test-pr-format.sh <pr-body-file> [review-comment-file]
# Exit: 0 = all pass, 1 = mandatory failures, 2 = usage error
# Trust boundary: accepts local file paths from the caller. Files are read
# but never executed. Paths with shell metacharacters are safely quoted.

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

FAIL=0
WARN=0

fail() { echo -e "${RED}FAIL${NC}: $1"; FAIL=$((FAIL + 1)); }
warn() { echo -e "${YELLOW}WARN${NC}: $1"; WARN=$((WARN + 1)); }
pass() { echo -e "${GREEN}PASS${NC}: $1"; }

if [[ $# -lt 1 ]]; then
    echo "Usage: bash $0 <pr-body-file> [review-comment-file]"
    exit 2
fi

PR_BODY="$1"
REVIEW_COMMENT="${2:-}"

if [[ ! -f "$PR_BODY" ]]; then
    echo "File not found: $PR_BODY"
    exit 2
fi

echo "=== PR Body: $PR_BODY ==="

# --- PR Body Checks ---

# Starts with ## Summary
if head -1 "$PR_BODY" | grep -q "^## Summary"; then
    pass "Starts with ## Summary"
else
    fail "Does not start with ## Summary"
fi

# Summary is one paragraph (no blank lines before next ##)
# Allow one blank line after heading (standard markdown), but not within the paragraph
SUMMARY_END=$(awk '/^## /{if(NR>1){print NR-1; exit}} END{print NR}' "$PR_BODY" | head -1)
# Start from line 4 (skip heading + blank line + first content line) to check for extra blanks
if [[ "$SUMMARY_END" -gt 4 ]]; then
    SUMMARY_BLANKS=$(sed -n "4,${SUMMARY_END}p" "$PR_BODY" | grep -c '^$' || true)
else
    SUMMARY_BLANKS=0
fi
if [[ "$SUMMARY_BLANKS" -eq 0 ]]; then
    pass "Summary is one paragraph"
else
    fail "Summary has blank lines (multiple paragraphs)"
fi

# Summary sentence count (approximate: count periods, !, ?)
# Known limitation: miscounts abbreviations (Dr., e.g.) and decimals as sentence boundaries
SUMMARY_TEXT=$(sed -n "3,${SUMMARY_END}p" "$PR_BODY")
SENTENCE_COUNT=$(echo "$SUMMARY_TEXT" | awk '{n=gsub(/[.!?]+/,"&"); total+=n} END{print total+0}')
if [[ "$SENTENCE_COUNT" -ge 3 && "$SENTENCE_COUNT" -le 5 ]]; then
    pass "Summary has $SENTENCE_COUNT sentences (target: 3-5)"
elif [[ "$SENTENCE_COUNT" -ge 2 && "$SENTENCE_COUNT" -le 7 ]]; then
    warn "Summary has $SENTENCE_COUNT sentences (target: 3-5)"
else
    fail "Summary has $SENTENCE_COUNT sentences (target: 3-5)"
fi

# ## Changes section exists
if grep -q "^## Changes" "$PR_BODY"; then
    pass "## Changes section exists"
else
    fail "## Changes section missing"
fi

# Change bullets start with **
if grep -A1 "^## Changes" "$PR_BODY" | grep -q '^\- \*\*'; then
    pass "Change bullets start with **bold file path**"
elif grep -q '^\- \*\*' "$PR_BODY"; then
    pass "Change bullets start with **bold file path**"
else
    warn "Change bullets do not start with **bold file path**"
fi

# ## Test plan section exists
if grep -q "^## Test plan" "$PR_BODY"; then
    pass "## Test plan section exists"
else
    fail "## Test plan section missing"
fi

# At least one checked box
if grep -q '\- \[x\]' "$PR_BODY"; then
    CHECKED=$(grep -c '\- \[x\]' "$PR_BODY" || true)
    pass "$CHECKED checked checkbox(es) found"
else
    fail "No checked checkboxes in test plan"
fi

# Coverage notes subsection
if grep -q "\*\*Coverage notes:\*\*" "$PR_BODY"; then
    pass "**Coverage notes:** subsection exists"
else
    fail "**Coverage notes:** subsection missing"
fi

# ## Notes section exists
if grep -q "^## Notes" "$PR_BODY"; then
    pass "## Notes section exists"
else
    fail "## Notes section missing"
fi

# No ## Gate Evidence
if grep -q "^## Gate Evidence" "$PR_BODY"; then
    fail "## Gate Evidence section should not exist (redundant with test plan)"
else
    pass "No ## Gate Evidence section"
fi

# Sentence length check (warn only) — simplified for macOS compatibility
LONG_SENTENCES=$(awk '/^[^#*>-]/ && length>150{print NR": "$0}' "$PR_BODY" | head -5)
if [[ -n "$LONG_SENTENCES" ]]; then
    warn "Some lines exceed 150 chars (may contain long sentences):"
    echo "$LONG_SENTENCES" | sed 's/^/  /'
else
    pass "No unusually long lines"
fi

# Contraction check (warn only)
CONTRACTIONS=$(grep -nE "'(ll|re|s|ve|d|t) " "$PR_BODY" | head -5 || true)
if [[ -n "$CONTRACTIONS" ]]; then
    warn "Contractions found (first 5):"
    echo "$CONTRACTIONS" | sed 's/^/  /'
else
    pass "No contractions found"
fi

# Banned filler words
FILLER=$(grep -inE "(it is worth noting|importantly|simply|just|easily|seamlessly)" "$PR_BODY" | head -5 || true)
if [[ -n "$FILLER" ]]; then
    fail "Banned filler words found:"
    echo "$FILLER" | sed 's/^/  /'
else
    pass "No banned filler words"
fi

# Internal skill names (maintain this list when new skills are added)
INTERNAL=$(grep -inE "(GNHF|toren|breq|applytime)" "$PR_BODY" | head -5 || true)
if [[ -n "$INTERNAL" ]]; then
    fail "Internal skill names found in PR body:"
    echo "$INTERNAL" | sed 's/^/  /'
else
    pass "No internal skill names"
fi

# --- Review Comment Checks ---

if [[ -n "$REVIEW_COMMENT" ]]; then
    if [[ ! -f "$REVIEW_COMMENT" ]]; then
        fail "Review comment file not found: $REVIEW_COMMENT"
    elif [[ ! -s "$REVIEW_COMMENT" ]]; then
        fail "Review comment file is empty: $REVIEW_COMMENT"
    else
        echo ""
        echo "=== Review Comment: $REVIEW_COMMENT ==="

    # Starts with ## Code Review
    if head -1 "$REVIEW_COMMENT" | grep -q "^## Code Review"; then
        pass "Starts with ## Code Review"
    else
        fail "Does not start with ## Code Review"
    fi

    # Has a markdown table with correct headers
    if grep -q "^| # | Severity | Finding | Fix |" "$REVIEW_COMMENT"; then
        pass "Table has correct columns: #, Severity, Finding, Fix"
    elif grep -q "| Severity |" "$REVIEW_COMMENT"; then
        warn "Table has Severity column but header format may differ"
    else
        fail "Table missing required columns (#, Severity, Finding, Fix)"
    fi

    # No posture column
    if grep -qE "\| (SWE|QA|DevOps|Security|Arch) \|" "$REVIEW_COMMENT"; then
        fail "Posture column found (should be removed)"
    else
        pass "No posture column"
    fi

    # Severity values are valid
    INVALID_SEV=$(grep -oE '\| P[1-4] [A-Z]+ \|' "$REVIEW_COMMENT" | sort -u | grep -vE '\| (P1 CRITICAL|P2 MAJOR|P3 MINOR|P4 NIT) \|' || true)
    if [[ -n "$INVALID_SEV" ]]; then
        fail "Invalid severity values found:"
        echo "$INVALID_SEV" | sed 's/^/  /'
    else
        pass "All severity values are valid"
    fi

    # Fix column is not empty
    EMPTY_FIX=$(awk -F'|' '/^\| *[0-9]+/{gsub(/^[ \t]+|[ \t]+$/,"",$5); if($5=="" || $5==" ") print NR": empty Fix column"}' "$REVIEW_COMMENT" | head -5)
    if [[ -n "$EMPTY_FIX" ]]; then
        fail "Empty Fix column entries:"
        echo "$EMPTY_FIX" | sed 's/^/  /'
    else
        pass "All Fix columns are filled"
    fi

    # Result line exists
    if grep -q 'Result:' "$REVIEW_COMMENT"; then
        pass "**Result:** line exists"
    else
        fail "**Result:** line missing"
    fi

    # Edge case verification subsection exists
    if grep -q "### Edge case verification" "$REVIEW_COMMENT"; then
        pass "### Edge case verification subsection exists"
    else
        warn "### Edge case verification subsection missing (recommended by template)"
    fi

    # Result line severity counts match table rows
    RESULT_LINE=$(grep 'Result:' "$REVIEW_COMMENT" | head -1)
    TABLE_ROWS=$(grep -cE '^\| [0-9]+ \| P[1-4]' "$REVIEW_COMMENT" || true)
    RESULT_TOTAL=$(echo "$RESULT_LINE" | awk '{for(i=1;i<=NF;i++) if($i ~ /^[0-9]+$/) total+=$i} END{print total+0}')
    if [[ "$RESULT_TOTAL" -gt 0 && "$RESULT_TOTAL" -ne "$TABLE_ROWS" ]]; then
        warn "Result line reports $RESULT_TOTAL findings but table has $TABLE_ROWS rows"
    elif [[ "$RESULT_TOTAL" -eq 0 && "$TABLE_ROWS" -gt 0 ]]; then
        warn "Result line reports 0 findings but table has $TABLE_ROWS rows"
    else
        pass "Result line counts match table rows ($TABLE_ROWS)"
    fi
    fi
else
    echo ""
    echo "(No review comment file provided, skipping review comment checks)"
fi

# --- Summary ---
echo ""
echo "=== Summary ==="
echo -e "Failures: ${FAIL}"
echo -e "Warnings: ${WARN}"

if [[ "$FAIL" -gt 0 ]]; then
    echo -e "${RED}FAILED${NC} — fix mandatory issues before posting"
    exit 1
else
    echo -e "${GREEN}PASSED${NC} — ready to post (check warnings if any)"
    exit 0
fi
