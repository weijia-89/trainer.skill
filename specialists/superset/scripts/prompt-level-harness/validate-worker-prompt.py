#!/usr/bin/env python3
# Prompt-level falsifier validator for H5 (worktree first command).
#
# Reads a worker-prompt markdown file, detects which of three valid shapes
# it uses to resolve H5, and reports PASS or structured-error FAIL.
#
# Shape A: Worktree setup (default). Prompt contains a `git worktree add`
#   invocation, names a worktree path under `.worktrees/<slug>`, and the
#   slug serves as the sibling-distinct identifier.
#
# Shape B: Same-tree exception. Prompt explicitly states same-tree dispatch,
#   enumerates the four v0.5.0 Proposal 2 preconditions (single-file,
#   read-mostly, no parallel work, no gated-doc edits), includes the two
#   v0.5.0 Proposal 3 mandatory commands as the first two run_command calls
#   (`git -C <project> branch --show-current` and `git -C <project> status
#   --short`), and includes the escalation-void clause.
#
# Shape C: No-git exception (new, 2026-05-19 emergent). Prompt explicitly
#   states the project is not a git repository AND documents the
#   parallel-collision-mitigation strategy (disjoint owned_paths across
#   sibling agents).
#
# Usage:
#   python3 validate-worker-prompt.py <path-to-worker-prompt.md> [--project-type git|no-git]
#
# Exit code: 0 on PASS; 1 on FAIL (structured-error JSON emitted to stderr).
#            2 on usage / IO error.
#
# Stdlib only: no PyYAML, no requests, no third-party imports.

import argparse
import json
import re
import sys
from pathlib import Path


# Canonical regex patterns for each shape. Tuned for the realistic prompt
# vocabulary used in superset templates, with flexibility for synonyms.

# Shape A markers
RE_WORKTREE_ADD = re.compile(r"git\s+(?:-C\s+\S+\s+)?worktree\s+add", re.IGNORECASE)
RE_WORKTREE_PATH = re.compile(r"\.worktrees/([A-Za-z0-9][\w\-]*)")

# Shape B markers
RE_SAME_TREE = re.compile(
    r"(?:same[- ]tree\s+(?:exception|dispatch)|skip(?:ping)?\s+the\s+worktree"
    r"|no\s+worktree)",
    re.IGNORECASE,
)
RE_PRECONDITION_SINGLE_FILE = re.compile(r"single[- ]file", re.IGNORECASE)
RE_PRECONDITION_READ_MOSTLY = re.compile(r"read[- ]mostly", re.IGNORECASE)
RE_PRECONDITION_NO_PARALLEL = re.compile(
    r"no\s+parallel\s+work", re.IGNORECASE,
)
RE_PRECONDITION_NO_GATED = re.compile(
    r"no\s+gated[- ]doc(?:ument)?\s+edit|no\s+docs/specs\s+edit"
    r"|no\s+gated[- ]doc(?:ument)?s?\b",
    re.IGNORECASE,
)
RE_MANDATORY_BRANCH = re.compile(
    r"git\s+-C\s+\S+\s+branch\s+--show-current", re.IGNORECASE,
)
RE_MANDATORY_STATUS = re.compile(
    r"git\s+-C\s+\S+\s+status\s+--short", re.IGNORECASE,
)
RE_ESCALATION_VOID = re.compile(
    r"(?:exception\s+voids?|escalat\w+\s+(?:to|and).{0,40}(?:halt|operator)"
    r"|halts?\s+and\s+escalat\w+|task\s+escalates?\s+mid[- ]flight)",
    re.IGNORECASE,
)

# Shape C markers
RE_NO_GIT = re.compile(
    r"(?:not\s+a\s+git\s+repo(?:sitory)?|project\s+is\s+not\s+git[- ]tracked"
    r"|no[- ]git\s+(?:exception|context|project))",
    re.IGNORECASE,
)
RE_DISJOINT_OWNED = re.compile(
    r"disjoint\s+owned[_ ]paths?|owned[_ ]paths?\s+(?:are\s+)?disjoint"
    r"|disjoint\s+(?:per[- ]agent\s+)?paths?\s+across\s+sibling",
    re.IGNORECASE,
)


def validate_shape_a(text):
    """Return (matched, missing_subpatterns) for Shape A."""
    missing = []
    if not RE_WORKTREE_ADD.search(text):
        missing.append("git_worktree_add_invocation")
    path_match = RE_WORKTREE_PATH.search(text)
    if not path_match:
        missing.append("worktree_path_with_slug")
    return (len(missing) == 0, missing, path_match.group(1) if path_match else None)


def validate_shape_b(text):
    """Return (matched, missing_subpatterns) for Shape B."""
    missing = []
    if not RE_SAME_TREE.search(text):
        missing.append("same_tree_declaration")
    if not RE_PRECONDITION_SINGLE_FILE.search(text):
        missing.append("precondition_single_file")
    if not RE_PRECONDITION_READ_MOSTLY.search(text):
        missing.append("precondition_read_mostly")
    if not RE_PRECONDITION_NO_PARALLEL.search(text):
        missing.append("precondition_no_parallel_work")
    if not RE_PRECONDITION_NO_GATED.search(text):
        missing.append("precondition_no_gated_doc_edits")
    if not RE_MANDATORY_BRANCH.search(text):
        missing.append("mandatory_command_branch_show_current")
    if not RE_MANDATORY_STATUS.search(text):
        missing.append("mandatory_command_status_short")
    if not RE_ESCALATION_VOID.search(text):
        missing.append("escalation_void_clause")
    return (len(missing) == 0, missing)


def validate_shape_c(text):
    """Return (matched, missing_subpatterns) for Shape C."""
    missing = []
    if not RE_NO_GIT.search(text):
        missing.append("no_git_declaration")
    if not RE_DISJOINT_OWNED.search(text):
        missing.append("disjoint_owned_paths_mitigation")
    return (len(missing) == 0, missing)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a worker prompt against H5 (worktree first command).",
    )
    parser.add_argument(
        "prompt_path",
        type=Path,
        help="Path to the worker prompt markdown file.",
    )
    parser.add_argument(
        "--project-type",
        choices=["git", "no-git"],
        default=None,
        help="Optional hint about project type. If 'no-git', only Shape C is valid.",
    )
    args = parser.parse_args()

    if not args.prompt_path.is_file():
        print(
            json.dumps(
                {
                    "falsifier": "H5",
                    "result": "IO_ERROR",
                    "message": f"prompt file not found: {args.prompt_path}",
                },
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        text = args.prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            json.dumps(
                {
                    "falsifier": "H5",
                    "result": "IO_ERROR",
                    "message": str(exc),
                },
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    # Score each shape.
    a_match, a_missing, a_slug = validate_shape_a(text)
    b_match, b_missing = validate_shape_b(text)
    c_match, c_missing = validate_shape_c(text)

    # If --project-type=no-git is supplied, only Shape C is valid.
    if args.project_type == "no-git":
        if c_match:
            print(f"PASS H5: shape-C no-git exception, disjoint owned_paths documented")
            sys.exit(0)
        print(
            json.dumps(
                {
                    "falsifier": "H5",
                    "result": "FAIL",
                    "project_type_hint": "no-git",
                    "shape_c_missing": c_missing,
                },
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    # General path: any of the three shapes is acceptable.
    if a_match:
        print(f"PASS H5: shape-A worktree setup, slug={a_slug}")
        sys.exit(0)
    if b_match:
        print(f"PASS H5: shape-B same-tree exception, all 4 preconditions + mandatory commands + escalation-void clause present")
        sys.exit(0)
    if c_match:
        print(f"PASS H5: shape-C no-git exception, disjoint owned_paths documented")
        sys.exit(0)

    # All three failed; emit per-shape diagnostic.
    print(
        json.dumps(
            {
                "falsifier": "H5",
                "result": "FAIL",
                "shape_a_missing": a_missing,
                "shape_b_missing": b_missing,
                "shape_c_missing": c_missing,
                "hint": (
                    "Resolve H5 by satisfying one of the three shapes: "
                    "(A) worktree setup with `git worktree add` and `.worktrees/<slug>` path, "
                    "(B) same-tree exception with all 4 preconditions, both mandatory commands, "
                    "and escalation-void clause, or "
                    "(C) no-git exception with disjoint owned_paths mitigation."
                ),
            },
            indent=2,
        ),
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
