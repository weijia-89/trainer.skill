#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=trainer_gh_repo.sh
source "$ROOT/scripts/trainer_gh_repo.sh"

assert_eq() {
  local got expect label
  got=$1 expect=$2 label=$3
  if [[ "$got" != "$expect" ]]; then
    echo "FAIL $label: got '$got' want '$expect'" >&2
    exit 1
  fi
}

assert_fail() {
  local remote=$1 label=$2
  if trainer_gh_repo_from_remote "$remote"; then
    echo "FAIL $label: expected parse failure for '$remote'" >&2
    exit 1
  fi
}

assert_eq "$(trainer_gh_repo_from_remote 'https://github.com/weijia-89/trainer.skill.git')" \
  'weijia-89/trainer.skill' 'https trainer.skill'
assert_eq "$(trainer_gh_repo_from_remote 'git@github.com:weijia-89/trainer.skill.git')" \
  'weijia-89/trainer.skill' 'ssh trainer.skill'
assert_eq "$(trainer_gh_repo_from_remote 'https://github.com/weijia-89/toebeans.git')" \
  'weijia-89/toebeans' 'https toebeans'
assert_fail 'https://github.com/weijia-89' 'owner only'

echo 'test_trainer_gh_repo: ok'
