#!/usr/bin/env bash
# Run base banned-vocab regex against the skill's own content.
# The skill must obey its own voice rules. Acceptance: 0 hits in skill content.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/test_banned_vocab.sh"
