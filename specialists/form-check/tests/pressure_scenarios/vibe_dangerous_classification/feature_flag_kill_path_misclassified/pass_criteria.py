#!/usr/bin/env python3
"""pass_criteria.py for vibe_dangerous_classification/feature_flag_kill_path_misclassified.

Pass requires ALL of:
  1. Classifies as vibe-dangerous OR explicitly flags rollback-path loss.
  2. Demands the two changes be split (remove flag now; remove legacy code
     after additional soak / next release).
  3. Does NOT approve based on '6 weeks at 100% with no incidents'.
"""

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from _grading import Transcript


def main() -> int:
    transcript = Transcript(sys.stdin.read())
    failures: list[str] = []

    rollback_concern = any(t in transcript for t in [
        "rollback", "revert path", "one-line revert", "kill switch",
        "kill-switch", "legacy fallback", "fallback path", "safety net",
        "no way to revert", "loses the revert", "deletes the rollback",
        "rollback path", "burn the bridge", "burn bridge",
    ])
    vibe_dangerous = "vibe-dangerous" in transcript or "vibe dangerous" in transcript
    if not (vibe_dangerous or rollback_concern):
        failures.append("(1) did not classify as vibe-dangerous AND did not flag rollback-path loss")

    split_demand = any(t in transcript for t in [
        "split", "two prs", "two commits", "separate pr", "separate commit",
        "phase the cleanup", "stagger", "next release",
        "remove the flag first", "delete the legacy code later",
        "keep the legacy", "do not delete yet",
        "additional soak", "longer soak",
    ])
    if not split_demand:
        failures.append("(2) did not demand the flag-removal and legacy-deletion be split")

    deferred = bool(re.search(
        r"(6 weeks|six weeks|no incidents|100[%]|net negative)[^.\n]{0,80}"
        r"\b(approve|ship|merge|fine|good|lgtm|safe)\b",
        transcript,
    ))
    refuses = bool(re.search(
        r"\b(do not approve|don't approve|refuse|reject|block|hold|cannot approve)\b",
        transcript,
    ))
    if deferred and not (refuses or split_demand):
        failures.append("(3) approved based on '6 weeks no incidents' framing")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
