#!/usr/bin/env python3
"""logbook: a per-project, append-only work ledger for trainer sessions.

Standard library only. No installs, no network.

Commands:
  init     --objective TEXT [--authority TEXT] [--non-goal TEXT] [--force-dir]
  record slice --what TEXT --scope TEXT [--evidence PATH | --no-evidence REASON]
  record outcome --outcome {missed,logged,pr} [--id ID | --latest]
  record next --what TEXT
  status
  verify

Exit codes:
  0 ok            1 verification failed   2 empty logbook   3 torn tail
  4 refused duplicate or unknown record   5 already initialized
  6 not initialized                        7 refused target  9 summary too long
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_OK = 0
EXIT_VERIFY_FAILED = 1
EXIT_EMPTY = 2
EXIT_TORN = 3
EXIT_DUPLICATE = 4
EXIT_ALREADY = 5
EXIT_NOT_INITIALIZED = 6
EXIT_REFUSED = 7
EXIT_TOO_LONG = 9

DIR_NAME = ".workledger"
LEDGER_NAME = "ledger.jsonl"
STATE_NAME = "ACTIVE_STATE.md"
LOCK_NAME = ".lock"
GITIGNORE_NAME = ".gitignore"
MAX_SUMMARY = 240
TORN_MARKER = "checkpoint-tail-unknown"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def event_id(body: dict) -> str:
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def project_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".git").exists():
            return candidate
    return here


def ledger_dir(root: Path) -> Path:
    return root / DIR_NAME


def ledger_path(root: Path) -> Path:
    return ledger_dir(root) / LEDGER_NAME


def state_path(root: Path) -> Path:
    return ledger_dir(root) / STATE_NAME


class Locked:
    """Exclusive advisory lock over one project ledger."""

    def __init__(self, root: Path) -> None:
        self.path = ledger_dir(root) / LOCK_NAME
        self.handle = None

    def __enter__(self):
        self.handle = open(self.path, "a+", encoding="utf-8")
        fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()
        self.handle = None
        return False


def read_events(root: Path) -> tuple[list[dict], bool]:
    """Return (events, torn). A torn tail means the last record is incomplete."""
    path = ledger_path(root)
    if not path.is_file():
        return [], False
    raw = path.read_bytes()
    if not raw:
        return [], False
    torn = not raw.endswith(b"\n")
    lines = raw.decode("utf-8", errors="replace").splitlines()
    if torn:
        lines = lines[:-1]
    events = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            raise ValueError(f"corrupt record at line {number}")
    return events, torn


def read_events_or_fail(root: Path) -> tuple[list[dict], bool] | None:
    """Read the ledger. Returns None (after reporting) when a record is corrupt."""
    try:
        return read_events(root)
    except ValueError as error:
        print(f"{TORN_MARKER}: {error}", file=sys.stderr)
        return None


def repair_tail(root: Path) -> bool:
    """Drop an incomplete final record. Call only while holding the lock."""
    path = ledger_path(root)
    if not path.is_file():
        return False
    raw = path.read_bytes()
    if not raw or raw.endswith(b"\n"):
        return False
    cut = raw.rfind(b"\n") + 1
    with path.open("r+b") as handle:
        handle.truncate(cut)
        handle.flush()
        os.fsync(handle.fileno())
    print("repaired torn tail: dropped an incomplete final record", file=sys.stderr)
    return True


def append_event(root: Path, body: dict) -> dict:
    """Append one event. Call only while holding the lock."""
    event = {"ts": body["ts"], "kind": body["kind"], "id": event_id(body)}
    for key, value in body.items():
        if key not in event:
            event[key] = value
    with ledger_path(root).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return event


def latest_goal(events: list[dict]) -> dict | None:
    goals = [e for e in events if e.get("kind") == "goal_registered"]
    return goals[-1] if goals else None


def outcome_for(events: list[dict], slice_id: str) -> dict | None:
    for event in events:
        if event.get("kind") == "outcome" and event.get("slice_id") == slice_id:
            return event
    return None


def write_state(root: Path, events: list[dict]) -> None:
    goal = latest_goal(events)
    slices = [e for e in events if e.get("kind") == "slice"]
    nexts = [e for e in events if e.get("kind") == "next"]
    tally = {"logged": 0, "missed": 0, "pr": 0}
    lines = [
        "# ACTIVE STATE (generated by logbook; do not edit by hand)",
        "",
        "## Objective",
        (goal or {}).get("objective", "not recorded"),
        "",
        "## Non-Goals",
    ]
    non_goals = (goal or {}).get("non_goals") or []
    lines.extend([f"- {item}" for item in non_goals] or ["- (none recorded)"])
    lines.extend(["", "## Next set on the bar"])
    lines.append(nexts[-1]["what"] if nexts else "not set - record the next one")
    lines.extend(["", "## Recent sets"])
    for event in slices[-10:]:
        mark = outcome_for(events, event["id"])
        outcome = mark["outcome"] if mark else "unlogged"
        if "evidence" in event:
            proof = event["evidence"]
        else:
            proof = f"UNVERIFIED: {event.get('evidence_reason', 'no reason recorded')}"
        lines.append(
            f"- {event['ts']} | {event['what']} | scope: {event['scope']} "
            f"| outcome: {outcome} | evidence: {proof}"
        )
    if not slices:
        lines.append("- (no sets logged yet)")
    for event in events:
        if event.get("kind") == "outcome":
            tally[event["outcome"]] = tally.get(event["outcome"], 0) + 1
    lines.extend(
        ["", "## Outcome tally", f"- logged: {tally['logged']}, missed: {tally['missed']}, pr: {tally['pr']}"]
    )
    target = state_path(root)
    temp = target.with_name(target.name + ".tmp")
    temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temp, target)


def normalize_evidence(root: Path, raw: str) -> str:
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return str(candidate)
    resolved = (root / candidate).resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return raw


def cmd_init(args) -> int:
    root = project_root(args.project)
    if not args.force_dir:
        if root == Path.home().resolve() or root == Path(root.anchor):
            print("refused: refusing to open a logbook at the home directory", file=sys.stderr)
            return EXIT_REFUSED
        if not (root / ".git").exists():
            print("refused: target is not a git project (use --force-dir to override)", file=sys.stderr)
            return EXIT_REFUSED
    if not root.is_dir():
        print("refused: target directory does not exist", file=sys.stderr)
        return EXIT_REFUSED
    directory = ledger_dir(root)
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass
    except OSError as error:
        print(f"refused: cannot create {directory}: {error}", file=sys.stderr)
        return EXIT_REFUSED
    body = {
        "ts": now(),
        "kind": "goal_registered",
        "objective": args.objective.strip(),
        "authority": args.authority or [],
        "non_goals": args.non_goal or [],
    }
    with Locked(root):
        loaded = read_events_or_fail(root)
        if loaded is None:
            return EXIT_TORN
        events, _ = loaded
        if events:
            print("refused: this project already has a logbook", file=sys.stderr)
            return EXIT_ALREADY
        gitignore = directory / GITIGNORE_NAME
        if not gitignore.exists():
            gitignore.write_text("*\n", encoding="utf-8")
        event = append_event(root, body)
        write_state(root, [event])
    print(f"logbook opened at {ledger_dir(root)}")
    print(f"goal {event['id']}: {event['objective']}")
    return EXIT_OK


def require_logbook(root: Path) -> int | None:
    if not ledger_path(root).is_file():
        print("no logbook here: run init first", file=sys.stderr)
        return EXIT_NOT_INITIALIZED
    return None


def cmd_record_slice(args) -> int:
    root = project_root(args.project)
    missing = require_logbook(root)
    if missing is not None:
        return missing
    what = args.what.strip()
    scope = args.scope.strip()
    if not what or not scope:
        print("refused: a set needs both --what and --scope", file=sys.stderr)
        return EXIT_DUPLICATE
    if len(what) > MAX_SUMMARY or len(scope) > MAX_SUMMARY:
        print(f"refused: summaries cap at {MAX_SUMMARY} characters", file=sys.stderr)
        return EXIT_TOO_LONG
    if args.evidence and args.no_evidence:
        print("refused: pass --evidence or --no-evidence, not both", file=sys.stderr)
        return EXIT_DUPLICATE
    with Locked(root):
        repair_tail(root)
        loaded = read_events_or_fail(root)
        if loaded is None:
            return EXIT_TORN
        events, _ = loaded
        goal = latest_goal(events)
        if goal is None:
            print("no logbook here: run init first", file=sys.stderr)
            return EXIT_NOT_INITIALIZED
        for event in events:
            if event.get("kind") == "slice" and event.get("what") == what and event.get("scope") == scope:
                print(f"refused: that set is already logged ({event['id']})", file=sys.stderr)
                return EXIT_DUPLICATE
        body = {
            "ts": now(),
            "kind": "slice",
            "goal_id": goal["id"],
            "what": what,
            "scope": scope,
        }
        if args.evidence:
            body["evidence"] = normalize_evidence(root, args.evidence)
        else:
            body["evidence_reason"] = (args.no_evidence or "").strip() or "no evidence recorded"
        event = append_event(root, body)
        events.append(event)
        write_state(root, events)
    print(f"set logged {event['id']}: {event['what']}")
    return EXIT_OK


def cmd_record_outcome(args) -> int:
    root = project_root(args.project)
    missing = require_logbook(root)
    if missing is not None:
        return missing
    if args.id and args.latest:
        print("refused: name one set with --id, or ask for --latest, not both", file=sys.stderr)
        return EXIT_DUPLICATE
    with Locked(root):
        repair_tail(root)
        loaded = read_events_or_fail(root)
        if loaded is None:
            return EXIT_TORN
        events, _ = loaded
        slices = [e for e in events if e.get("kind") == "slice"]
        if not slices:
            print("refused: no sets logged yet", file=sys.stderr)
            return EXIT_DUPLICATE
        if args.id:
            target = next((e for e in slices if e["id"] == args.id), None)
            if target is None:
                print(f"refused: no set with id {args.id}", file=sys.stderr)
                return EXIT_DUPLICATE
        else:
            target = slices[-1]
        if outcome_for(events, target["id"]) is not None:
            print(f"refused: set {target['id']} already has an outcome", file=sys.stderr)
            return EXIT_DUPLICATE
        body = {
            "ts": now(),
            "kind": "outcome",
            "goal_id": target["goal_id"],
            "slice_id": target["id"],
            "outcome": args.outcome,
        }
        event = append_event(root, body)
        events.append(event)
        write_state(root, events)
    print(f"outcome {args.outcome} recorded for set {target['id']}")
    return EXIT_OK


def cmd_record_next(args) -> int:
    root = project_root(args.project)
    missing = require_logbook(root)
    if missing is not None:
        return missing
    what = args.what.strip()
    if not what:
        print("refused: the next set needs --what", file=sys.stderr)
        return EXIT_DUPLICATE
    if len(what) > MAX_SUMMARY:
        print(f"refused: summaries cap at {MAX_SUMMARY} characters", file=sys.stderr)
        return EXIT_TOO_LONG
    with Locked(root):
        repair_tail(root)
        loaded = read_events_or_fail(root)
        if loaded is None:
            return EXIT_TORN
        events, _ = loaded
        goal = latest_goal(events)
        if goal is None:
            print("no logbook here: run init first", file=sys.stderr)
            return EXIT_NOT_INITIALIZED
        body = {"ts": now(), "kind": "next", "goal_id": goal["id"], "what": what}
        event = append_event(root, body)
        events.append(event)
        write_state(root, events)
    print(f"next set recorded: {event['what']}")
    return EXIT_OK


def cmd_status(args) -> int:
    root = project_root(args.project)
    missing = require_logbook(root)
    if missing is not None:
        return missing
    with Locked(root):
        loaded = read_events_or_fail(root)
        if loaded is None:
            return EXIT_TORN
        events, torn = loaded
        if torn:
            print(
                f"{TORN_MARKER}: the last record is incomplete; not trusting the log",
                file=sys.stderr,
            )
            return EXIT_TORN
        write_state(root, events)
    goal = latest_goal(events)
    slices = [e for e in events if e.get("kind") == "slice"]
    nexts = [e for e in events if e.get("kind") == "next"]
    print(f"objective: {(goal or {}).get('objective', 'not recorded')}")
    print(f"sets logged: {len(slices)}")
    print(f"next set on the bar: {nexts[-1]['what'] if nexts else 'not set'}")
    return EXIT_OK


def cmd_verify(args) -> int:
    root = project_root(args.project)
    missing = require_logbook(root)
    if missing is not None:
        return missing
    with Locked(root):
        loaded = read_events_or_fail(root)
        if loaded is None:
            return EXIT_TORN
        events, torn = loaded
        if torn:
            print(
                f"{TORN_MARKER}: the last record is incomplete; not trusting the log",
                file=sys.stderr,
            )
            return EXIT_TORN
    slices = [e for e in events if e.get("kind") == "slice"]
    if not slices:
        print("no sets logged yet: nothing to verify")
        return EXIT_EMPTY
    failures = 0
    for event in slices:
        label = event["what"]
        if "evidence" in event:
            raw = event["evidence"]
            path = Path(raw) if Path(raw).is_absolute() else root / raw
            if path.is_file():
                print(f"EV_OK         {label} | evidence={raw}")
                continue
            note = "" if not path.exists() else " (not a file)"
            print(f"EV_MISSING    {label} | evidence={raw}{note}")
            failures += 1
        else:
            reason = event.get("evidence_reason", "no reason recorded")
            print(f"EV_UNVERIFIED {label} | reason={reason}")
            failures += 1
    if not any(e.get("kind") == "next" for e in events):
        print("WARN  next set on the bar is not set", file=sys.stderr)
    if failures:
        print(f"{failures} set(s) without proof")
        return EXIT_VERIFY_FAILED
    print("all sets carry proof")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logbook", description="per-project work ledger")
    parser.add_argument("--project", default=None, help="project root (default: nearest git root)")
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("init", help="open a logbook for this project")
    init_parser.add_argument("--objective", required=True)
    init_parser.add_argument("--authority", action="append", default=[])
    init_parser.add_argument("--non-goal", action="append", default=[])
    init_parser.add_argument("--force-dir", action="store_true")

    record_parser = commands.add_parser("record", help="log a set, an outcome, or the next set")
    record_commands = record_parser.add_subparsers(dest="record_kind", required=True)

    slice_parser = record_commands.add_parser("slice", help="log one work slice")
    slice_parser.add_argument("--what", required=True)
    slice_parser.add_argument("--scope", required=True)
    slice_parser.add_argument("--evidence")
    slice_parser.add_argument("--no-evidence", dest="no_evidence")

    outcome_parser = record_commands.add_parser("outcome", help="tag a set")
    outcome_parser.add_argument("--outcome", required=True, choices=["missed", "logged", "pr"])
    outcome_parser.add_argument("--id", default=None)
    outcome_parser.add_argument("--latest", action="store_true")

    next_parser = record_commands.add_parser("next", help="name the next set")
    next_parser.add_argument("--what", required=True)

    commands.add_parser("status", help="refresh and print the current state")
    commands.add_parser("verify", help="form check every logged set")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        return cmd_init(args)
    if args.command == "status":
        return cmd_status(args)
    if args.command == "verify":
        return cmd_verify(args)
    if args.record_kind == "slice":
        return cmd_record_slice(args)
    if args.record_kind == "outcome":
        return cmd_record_outcome(args)
    return cmd_record_next(args)


if __name__ == "__main__":
    sys.exit(main())
