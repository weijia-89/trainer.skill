#!/usr/bin/env bash
# validate-track-status.sh - status-claim evidence validator for superset daily-log manifests.
#
# Usage: bash validate-track-status.sh <path-to-daily-log.md> [project-root]
#
# Parses the daily-log YAML frontmatter manifest, extracts each agent (track),
# and emits ~5 lines per track with branch / produces / manifest-status / last-activity
# evidence followed by a VERDICT line.
#
# Evidence taxonomy (per SKILL.md "Status-claim evidence iron law"):
#   PRIMARY:   git branch existence, files on disk at produces paths, branch HEAD timestamp
#   SECONDARY: manifest status field, narrative claims
#   N/A:       not-a-git-repo (no-git Shape C), no produces declared
#
# Verdicts:
#   valid-dispatch              status=DONE and produces all on disk (or DONE with branch when produces=[])
#   in-flight                   status=IN_PROGRESS|CLAIMED with branch or partial produces evidence
#   undispatched                status=PLANNED with no branch and no produces evidence
#   status-unverified           manifest status conflicts with primary evidence (DONE but produces absent)
#   blocked                     status=BLOCKED
#   failed                      status=FAILED
#   planned-but-evidence-present  status=PLANNED but branch or produces evidence exists (surface to operator)
#   unknown-status              status field unrecognized
#
# Exit codes:
#   0  all tracks emit (warnings on stderr if status-unverified rows surfaced)
#   1  no tracks parsed (manifest empty or unparseable)
#   2  usage error / missing daily-log
#
# Stdlib-only: bash, awk, sed, grep, git (optional, gracefully degrades on no-git projects).

set -euo pipefail

DAILY_LOG="${1:-}"
PROJECT_ROOT_ARG="${2:-}"

if [[ -z "$DAILY_LOG" ]]; then
  echo "usage: bash validate-track-status.sh <daily-log.md> [project-root]" >&2
  exit 2
fi

if [[ ! -f "$DAILY_LOG" ]]; then
  echo "error: daily-log not found: $DAILY_LOG" >&2
  exit 2
fi

if [[ -n "$PROJECT_ROOT_ARG" ]]; then
  PROJECT_ROOT="$PROJECT_ROOT_ARG"
else
  # Default: two parents up from daily log, matching validate-daily-log.py convention
  # (daily log at <project>/localonly/daily/<file>.md)
  PROJECT_ROOT="$(cd "$(dirname "$DAILY_LOG")/../.." && pwd)"
fi

# Detect git availability (Shape C no-git projects are valid; degrade gracefully)
GIT_AVAILABLE=0
if command -v git >/dev/null 2>&1 && git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  GIT_AVAILABLE=1
fi

# Extract YAML frontmatter (between first two `---` delimiter lines)
FRONTMATTER="$(awk '
  /^---[[:space:]]*$/ {
    c++
    if (c == 1) { next }
    if (c == 2) { exit }
  }
  c == 1 { print }
' "$DAILY_LOG")"

if [[ -z "$FRONTMATTER" ]]; then
  echo "error: no YAML frontmatter found in $DAILY_LOG (expected delimiters: ---)" >&2
  exit 1
fi

# Parse manifest into TSV: name<TAB>status<TAB>produces (semicolon-separated)
PARSED="$(printf '%s\n' "$FRONTMATTER" | awk '
  function trim(s) { sub(/^[[:space:]]+/, "", s); sub(/[[:space:]]+$/, "", s); return s }
  function flush() {
    if (current != "") {
      print current "\t" status "\t" produces
    }
  }
  BEGIN {
    in_agents = 0
    in_produces = 0
    current = ""
    status = "?"
    produces = ""
  }
  /^agents:[[:space:]]*$/ {
    in_agents = 1
    next
  }
  in_agents == 0 { next }
  # Top-level key (no leading space) ends the agents block
  /^[a-zA-Z_]/ {
    flush()
    in_agents = 0
    current = ""
    next
  }
  # New agent entry: "  - name: <slug>"
  /^[[:space:]]*-[[:space:]]+name:[[:space:]]+/ {
    flush()
    line = $0
    sub(/^[[:space:]]*-[[:space:]]+name:[[:space:]]+/, "", line)
    current = trim(line)
    status = "?"
    produces = ""
    in_produces = 0
    next
  }
  # status field
  /^[[:space:]]+status:[[:space:]]+/ {
    line = $0
    sub(/^[[:space:]]+status:[[:space:]]+/, "", line)
    status = trim(line)
    in_produces = 0
    next
  }
  # produces: [] (empty inline list)
  /^[[:space:]]+produces:[[:space:]]+\[\][[:space:]]*$/ {
    in_produces = 0
    next
  }
  # produces: (start block list)
  /^[[:space:]]+produces:[[:space:]]*$/ {
    in_produces = 1
    next
  }
  # In produces list: "      - <path>"
  in_produces == 1 && /^[[:space:]]+-[[:space:]]+/ {
    line = $0
    sub(/^[[:space:]]+-[[:space:]]+/, "", line)
    item = trim(line)
    if (produces == "") { produces = item } else { produces = produces ";" item }
    next
  }
  # Any other indented key ends produces list
  /^[[:space:]]+[a-zA-Z_]/ {
    in_produces = 0
    next
  }
  END { flush() }
')"

if [[ -z "$PARSED" ]]; then
  echo "error: no agents parsed from manifest in $DAILY_LOG" >&2
  exit 1
fi

# Track count of unverified status claims for stderr summary
UNVERIFIED_COUNT=0
TRACK_COUNT=0

# Process each track
while IFS=$'\t' read -r name status produces; do
  [[ -z "$name" ]] && continue
  TRACK_COUNT=$((TRACK_COUNT + 1))

  printf 'Track: %s\n' "$name"

  # --- Branch evidence (PRIMARY) ---
  branch_evidence="absent"
  branch_match=""
  head_sha=""
  if [[ $GIT_AVAILABLE -eq 1 ]]; then
    # Look for any branch (local or remote) whose name contains the agent name
    branch_match="$(git -C "$PROJECT_ROOT" branch -a --list "*${name}*" 2>/dev/null \
                    | head -1 | sed -e 's/^[* ]*//' -e 's|^remotes/||')"
    if [[ -n "$branch_match" ]]; then
      head_sha="$(git -C "$PROJECT_ROOT" rev-parse --short "$branch_match" 2>/dev/null || echo "?")"
      printf '  Branch HEAD: %s @ %s  [PRIMARY: dispatch evidence present]\n' "$branch_match" "$head_sha"
      branch_evidence="present"
    else
      printf '  Branch HEAD: <no branch matching *%s*>  [PRIMARY: no dispatch evidence]\n' "$name"
    fi
  else
    printf '  Branch HEAD: <git not available; no-git project>  [N/A: not a git repo]\n'
    branch_evidence="na"
  fi

  # --- Produces evidence (PRIMARY) ---
  produces_present=0
  produces_absent=0
  produces_status="none"
  if [[ -z "$produces" ]]; then
    printf '  Produces: <none declared>  [N/A: no produces in manifest]\n'
  else
    OLDIFS="$IFS"
    IFS=';'
    for p in $produces; do
      IFS="$OLDIFS"
      [[ -z "$p" ]] && { IFS=';'; continue; }
      if [[ "$p" == /* ]]; then
        full="$p"
      else
        full="$PROJECT_ROOT/$p"
      fi
      if [[ -e "$full" ]]; then
        printf '  Produces: %s: PRESENT  [PRIMARY: completion evidence on disk]\n' "$p"
        produces_present=$((produces_present + 1))
      else
        printf '  Produces: %s: ABSENT  [PRIMARY: no completion evidence]\n' "$p"
        produces_absent=$((produces_absent + 1))
      fi
      IFS=';'
    done
    IFS="$OLDIFS"
    if [[ $produces_absent -eq 0 ]]; then
      produces_status="all_present"
    elif [[ $produces_present -eq 0 ]]; then
      produces_status="all_absent"
    else
      produces_status="partial"
    fi
  fi

  # --- Manifest status (SECONDARY) ---
  printf '  Manifest status: %s  [SECONDARY]\n' "$status"

  # --- Last activity (PRIMARY, derived) ---
  if [[ "$branch_evidence" == "present" && $GIT_AVAILABLE -eq 1 ]]; then
    last_ts="$(git -C "$PROJECT_ROOT" log -1 --format='%cr' "$branch_match" 2>/dev/null || echo "unknown")"
    printf '  Last activity: %s (branch commit)  [PRIMARY: derived from git]\n' "$last_ts"
  elif [[ "$produces_status" == "all_present" || "$produces_status" == "partial" ]]; then
    printf '  Last activity: produces artifacts on disk  [PRIMARY: derived from produces existence]\n'
  else
    printf '  Last activity: never  [PRIMARY: derived from above]\n'
  fi

  # --- Verdict ---
  verdict="unknown-status"
  case "$status" in
    DONE)
      if [[ "$produces_status" == "all_present" ]]; then
        verdict="valid-dispatch"
      elif [[ "$produces_status" == "none" && "$branch_evidence" == "present" ]]; then
        verdict="valid-dispatch"
      elif [[ "$produces_status" == "none" && "$branch_evidence" == "na" ]]; then
        # No-git project with no produces declared; cannot verify either way
        verdict="status-unverified"
      else
        verdict="status-unverified"
      fi
      ;;
    IN_PROGRESS|CLAIMED)
      if [[ "$branch_evidence" == "present" ]]; then
        verdict="in-flight"
      elif [[ "$produces_status" == "partial" || "$produces_status" == "all_present" ]]; then
        verdict="in-flight"
      else
        verdict="status-unverified"
      fi
      ;;
    PLANNED|"NOT DISPATCHED"|NOT_DISPATCHED)
      if [[ "$branch_evidence" == "absent" || "$branch_evidence" == "na" ]] \
         && [[ "$produces_status" == "all_absent" || "$produces_status" == "none" ]]; then
        verdict="undispatched"
      else
        verdict="planned-but-evidence-present"
      fi
      ;;
    BLOCKED)
      verdict="blocked"
      ;;
    FAILED)
      verdict="failed"
      ;;
    *)
      verdict="unknown-status"
      ;;
  esac

  printf '  VERDICT: %s\n' "$verdict"
  printf '\n'

  if [[ "$verdict" == "status-unverified" || "$verdict" == "planned-but-evidence-present" ]]; then
    UNVERIFIED_COUNT=$((UNVERIFIED_COUNT + 1))
    printf 'WARN: track %s verdict=%s (manifest status conflicts with primary evidence)\n' \
      "$name" "$verdict" >&2
  fi
done <<< "$PARSED"

# Summary line
printf 'Validated %d track(s) in %s\n' "$TRACK_COUNT" "$DAILY_LOG"
if [[ $UNVERIFIED_COUNT -gt 0 ]]; then
  printf '  (%d unverified or evidence-conflicting; surface to operator)\n' "$UNVERIFIED_COUNT"
fi

exit 0
