#!/usr/bin/env bash
# Fixture-based test for tools/check_forcing_constraint.sh.
#
# Builds minimal repos in an isolated tmp dir and asserts the scanner's
# exit-code contract:
#   0 — at least one accepted forcing-constraint ADR with constraint_class
#   1 — no docs/adr/ OR no forcing-constraint ADR OR none accepted
#   2 — ADR exists but missing required keys (malformed)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "${SCRIPT_DIR}")"
TOOL="${SKILL_DIR}/tools/check_forcing_constraint.sh"

if [[ ! -f "${TOOL}" ]]; then
    echo "FAIL: tool not found at ${TOOL}" >&2
    exit 1
fi

WORK="$(mktemp -d -t wave9-fc-test.XXXXXX)"
cleanup() { rm -rf "${WORK}"; }
trap cleanup EXIT

pass=0
fail=0
assert_eq() {
    local got="$1" want="$2" name="$3"
    if [[ "${got}" != "${want}" ]]; then
        echo "  FAIL ${name}: want exit ${want}, got ${got}" >&2
        fail=$((fail + 1))
    else
        pass=$((pass + 1))
    fi
}

run_tool() {
    set +e
    bash "${TOOL}" "$1" >/dev/null 2>&1
    local rc=$?
    set -e
    echo "${rc}"
}

# --------------------------------------------------------------------
# Case 1: non-existent path → exit 1 (no docs/adr/)
# --------------------------------------------------------------------
assert_eq "$(run_tool "/tmp/wave9-fc-this-does-not-exist-xyz")" "1" "nonexistent_path"

# --------------------------------------------------------------------
# Case 2: repo exists but no docs/adr/ dir → exit 1
# --------------------------------------------------------------------
R2="${WORK}/no_adr_dir"
mkdir -p "${R2}/src"
echo "// code" > "${R2}/src/main.go"
assert_eq "$(run_tool "${R2}")" "1" "no_adr_dir"

# --------------------------------------------------------------------
# Case 3: docs/adr/ exists but is empty → exit 1
# --------------------------------------------------------------------
R3="${WORK}/empty_adr_dir"
mkdir -p "${R3}/docs/adr"
assert_eq "$(run_tool "${R3}")" "1" "empty_adr_dir"

# --------------------------------------------------------------------
# Case 4: ADRs exist but none are type=forcing-constraint → exit 1
# --------------------------------------------------------------------
R4="${WORK}/non_forcing_adrs"
mkdir -p "${R4}/docs/adr"
cat > "${R4}/docs/adr/0001-use-sqlite.md" <<'EOF'
# 0001 — use SQLite
- Status: accepted
- Type: technical
EOF
cat > "${R4}/docs/adr/0002-naming-convention.md" <<'EOF'
# 0002
- Status: accepted
- Type: convention
EOF
assert_eq "$(run_tool "${R4}")" "1" "no_forcing_type"

# --------------------------------------------------------------------
# Case 5: forcing-constraint + status=accepted + constraint_class → exit 0
# Uses canonical hyphen-prefixed key:value form.
# --------------------------------------------------------------------
R5="${WORK}/valid_forcing"
mkdir -p "${R5}/docs/adr"
cat > "${R5}/docs/adr/0007-multi-region.md" <<'EOF'
# 0007 — multi-region deployment

- Status: accepted
- Type: forcing-constraint
- Constraint_class: regulatory

GDPR Article 35 DPIA mandates EU-residency for personal data.
EOF
assert_eq "$(run_tool "${R5}")" "0" "valid_forcing_constraint"

# --------------------------------------------------------------------
# Case 6: forcing-constraint with status=proposed (not accepted) → exit 1
# --------------------------------------------------------------------
R6="${WORK}/proposed_only"
mkdir -p "${R6}/docs/adr"
cat > "${R6}/docs/adr/0008-microservices.md" <<'EOF'
# 0008 — microservices

- Status: proposed
- Type: forcing-constraint
- Constraint_class: scale-measured
EOF
assert_eq "$(run_tool "${R6}")" "1" "proposed_not_accepted"

# --------------------------------------------------------------------
# Case 7: forcing-constraint + accepted but MISSING constraint_class → exit 2 (malformed)
# --------------------------------------------------------------------
R7="${WORK}/missing_constraint_class"
mkdir -p "${R7}/docs/adr"
cat > "${R7}/docs/adr/0009-event-sourcing.md" <<'EOF'
# 0009 — event sourcing

- Status: accepted
- Type: forcing-constraint

(constraint_class line omitted on purpose)
EOF
assert_eq "$(run_tool "${R7}")" "2" "missing_constraint_class_is_malformed"

# --------------------------------------------------------------------
# Case 8: multiple ADRs, exactly one is valid forcing-constraint → exit 0
# --------------------------------------------------------------------
R8="${WORK}/multi_adr"
mkdir -p "${R8}/docs/adr"
cat > "${R8}/docs/adr/0001-use-sqlite.md" <<'EOF'
# 0001
- Status: accepted
- Type: technical
EOF
cat > "${R8}/docs/adr/0010-org-platform.md" <<'EOF'
# 0010 — adopt org platform team mandates
- Status: accepted
- Type: forcing-constraint
- Constraint_class: org-mandate
EOF
cat > "${R8}/docs/adr/0011-proposal.md" <<'EOF'
# 0011 — proposal
- Status: proposed
- Type: forcing-constraint
- Constraint_class: scale-measured
EOF
assert_eq "$(run_tool "${R8}")" "0" "one_valid_among_many"

# --------------------------------------------------------------------
# Case 9: forcing-constraint type with NO status line at all → exit 2 (malformed)
# --------------------------------------------------------------------
R9="${WORK}/no_status"
mkdir -p "${R9}/docs/adr"
cat > "${R9}/docs/adr/0012-no-status.md" <<'EOF'
# 0012

- Type: forcing-constraint
- Constraint_class: regulatory

Status line missing entirely.
EOF
assert_eq "$(run_tool "${R9}")" "2" "no_status_is_malformed"

# --------------------------------------------------------------------
# Case 10: case-insensitive status value (Accepted, ACCEPTED) → exit 0
# --------------------------------------------------------------------
R10="${WORK}/case_insensitive_status"
mkdir -p "${R10}/docs/adr"
cat > "${R10}/docs/adr/0013-uppercase.md" <<'EOF'
# 0013

- Status: ACCEPTED
- Type: forcing-constraint
- Constraint_class: regulatory
EOF
assert_eq "$(run_tool "${R10}")" "0" "uppercase_accepted_works"

# --------------------------------------------------------------------
# Case 11: lowercase keys (lowercase 'type:' / 'status:') accepted
# Algorithm spec lists this as a recognised form.
# --------------------------------------------------------------------
R11="${WORK}/lowercase_keys"
mkdir -p "${R11}/docs/adr"
cat > "${R11}/docs/adr/0014-yaml-style.md" <<'EOF'
# 0014 — YAML-style ADR

status: accepted
type: forcing-constraint
constraint_class: regulatory
EOF
assert_eq "$(run_tool "${R11}")" "0" "lowercase_keys_work"

# --------------------------------------------------------------------
# Case 12: non-md files in docs/adr/ ignored
# --------------------------------------------------------------------
R12="${WORK}/with_extra_files"
mkdir -p "${R12}/docs/adr"
echo "not an ADR" > "${R12}/docs/adr/README.txt"
echo '{"json": true}' > "${R12}/docs/adr/index.json"
cat > "${R12}/docs/adr/0015-real.md" <<'EOF'
- Status: accepted
- Type: forcing-constraint
- Constraint_class: regulatory
EOF
assert_eq "$(run_tool "${R12}")" "0" "non_md_files_ignored"

# --------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------
total=$((pass + fail))
if [[ "${fail}" -eq 0 ]]; then
    echo "test_forcing_constraint.sh: PASS (${pass}/${total} assertions)"
    exit 0
else
    echo "test_forcing_constraint.sh: FAIL (${fail}/${total} assertions failed)" >&2
    exit 1
fi
