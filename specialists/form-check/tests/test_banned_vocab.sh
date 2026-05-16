#!/usr/bin/env bash
# Verify base banned-vocab regex against fixtures, then run against skill content.
# Acceptance:
#   exit 0 if no base-banned vocab in skill markdown (excluding references/, examples/, tests/fixtures/)
#   exit 1 otherwise
#
# Words like "robust", "leverage", "harness", "elevate" have legitimate technical uses
# (agent harness, leverage-per-test, robust statistics, elevated incidence) and are
# caught only by per-archetype overlays. Base regex catches unambiguous AI-marketing.
# Quoted/backticked uses are excluded as meta-discussion (e.g. '"robust" → "powerful"').

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/test_banned_vocab.py"
