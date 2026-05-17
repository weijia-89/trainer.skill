#!/usr/bin/env bash
# prep_trial.sh <scenario_shortname> <condition>
#
# Copies the paste-region of the matching bundle (everything between
# === BEGIN_PASTE === and === END_PASTE ===, exclusive) to the macOS
# clipboard. Prints next steps to stdout.
#
# Args:
#   scenario_shortname  one of: 01_red-flag_upstream-constraint-missed
#                              02_test-as-spec_test-locks-in-bug
#                              03_hallucination_library-behavior-unverified
#   condition           baseline | treatment

set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -ne 2 ]]; then
  sed -n '2,15p' "$0" >&2
  exit 2
fi

SHORTNAME="$1"
CONDITION="$2"
BUNDLE="$KIT_DIR/bundles/$SHORTNAME/$CONDITION.txt"

if [[ ! -f "$BUNDLE" ]]; then
  echo "ERROR: bundle not found: $BUNDLE" >&2
  exit 2
fi

# Extract everything between markers, exclusive.
PAYLOAD="$(awk '/^=== BEGIN_PASTE ===$/{flag=1;next} /^=== END_PASTE ===$/{flag=0} flag' "$BUNDLE")"

if [[ -z "$PAYLOAD" ]]; then
  echo "ERROR: empty payload extracted from $BUNDLE" >&2
  exit 2
fi

if command -v pbcopy >/dev/null 2>&1; then
  printf '%s' "$PAYLOAD" | pbcopy
  BYTES="$(printf '%s' "$PAYLOAD" | wc -c | tr -d ' ')"
  LINES="$(printf '%s' "$PAYLOAD" | wc -l | tr -d ' ')"
  echo "Clipboard loaded: $SHORTNAME $CONDITION ($LINES lines, $BYTES bytes)"
  echo
  echo "Next steps:"
  echo "  1. Open a fresh temporary chat:"
  echo "     ChatGPT:  https://chatgpt.com/?temporary-chat=true"
  echo "     Gemini:   https://gemini.google.com/app  (then click 'New chat')"
  echo "  2. Paste (Cmd+V) and send."
  echo "  3. Wait for the full response."
  echo "  4. Select the entire response (Cmd+A inside the response area)."
  echo "  5. Copy (Cmd+C)."
  echo "  6. Save to a file under runs/<model>/<scenario_n>/<condition>.txt."
  echo "  7. Score:"
  echo "     bash manual_audit.sh $SHORTNAME <model-label> $CONDITION <response-file>"
else
  echo "ERROR: pbcopy not found (this kit assumes macOS)" >&2
  exit 2
fi
