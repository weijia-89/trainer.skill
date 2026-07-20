#!/usr/bin/env python3
"""Per-pass surface tracker for the autonomous code-review loop.

Records a per-pass "surface manifest" (files / symbols / verify exit codes
touched in a pass) under <root>/localonly/reviewer/<branch-slug>/ and gates
each subsequent pass on novelty: a pass must explore at least `novelty-min`
fraction of previously-unseen surface, otherwise the loop is re-traceable and
the stop condition is meaningless.

Stdlib only. No network. Read-only under --check.
"""
import argparse
import json
import os
import sys


def _norm(token):
    return os.path.normpath(token) if "/" in token or "\\" in token else token


def _load_manifest(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, ValueError):
        return None


def _manifest_path(root, branch, npass):
    return os.path.join(
        root, "localonly", "reviewer", branch, "pass{}.json".format(npass)
    )


def _union_surface(root, branch, upto):
    """Union of surface tokens across recorded passes 1..upto-1.

    Passes that were never recorded load as None and are skipped, so a gap
    in numbering does not corrupt the baseline.
    """
    surface = set()
    for n in range(1, upto):
        m = _load_manifest(_manifest_path(root, branch, n))
        if not m:
            continue
        for tok in m.get("surface", []):
            surface.add(_norm(tok))
    return surface


def record(args):
    if not args.surface:
        sys.stderr.write("record requires --surface tokens\n")
        return 2
    if args.pass_n < 1:
        sys.stderr.write("--pass must be >= 1\n")
        return 2
    path = _manifest_path(args.root, args.branch, args.pass_n)
    prior = _load_manifest(path)
    if prior is not None:
        # Guard against silent baseline corruption: re-recording an existing
        # pass overwrites the novelty baseline other passes depend on. Refuse
        # unless the surface is identical (idempotent re-run is harmless).
        if sorted(_norm(t) for t in prior.get("surface", [])) != sorted(
            _norm(t) for t in args.surface
        ):
            sys.stderr.write(
                "refusing to overwrite existing pass {} manifest "
                "(would corrupt novelty baseline)\n".format(args.pass_n)
            )
            return 2
    os.makedirs(os.path.dirname(path), exist_ok=True)
    manifest = {
        "pass": args.pass_n,
        "surface": sorted(_norm(t) for t in args.surface),
        "verify_exit_codes": args.verify or [],
    }
    if args.seed:
        manifest["seed"] = sorted(_norm(t) for t in args.seed)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    sys.stderr.write("recorded {}\n".format(path))
    return 0


def check(args):
    cur = _load_manifest(_manifest_path(args.root, args.branch, args.pass_n))
    if not cur:
        sys.stderr.write("no manifest for pass {}\n".format(args.pass_n))
        return 2
    surface = sorted(_norm(t) for t in cur.get("surface", []))
    if not surface:
        sys.stderr.write("empty surface rejected\n")
        return 2
    union = _union_surface(args.root, args.branch, args.pass_n)
    new = [t for t in surface if t not in union]
    novelty = len(new) / max(1, len(surface))
    if novelty < args.novelty_min:
        sys.stderr.write(
            "novelty {:.2f} < min {:.2f}; pass is re-traceable\n".format(
                novelty, args.novelty_min
            )
        )
        return 2
    # Explored-universe accounting (implements the loop's `unexplored == 0`
    # stop branch). The universe is the union of every pass's `seed` (the diff
    # + seed surface declared at record time). With no seed declared, the
    # universe is unknown and we report unexplored as None rather than guessing.
    seed = set()
    for n in range(1, args.pass_n + 1):
        m = _load_manifest(_manifest_path(args.root, args.branch, n))
        if m and m.get("seed"):
            seed.update(_norm(t) for t in m["seed"])
    unexplored = None
    if seed:
        explored = union | set(surface)
        unexplored = len(seed - explored)
    sys.stderr.write("novelty {:.2f} OK\n".format(novelty))
    if unexplored is not None:
        sys.stderr.write("unexplored {}\n".format(unexplored))
    return 0


def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=os.getcwd())
    common.add_argument("--branch", default=None)
    common.add_argument("--pass", dest="pass_n", type=int, default=None)
    p = argparse.ArgumentParser(description=__doc__, parents=[common])
    sub = p.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("record")
    rp.add_argument("--surface", nargs="+", default=[])
    rp.add_argument("--verify", nargs="*", type=int, default=[])
    rp.add_argument(
        "--seed",
        nargs="*",
        default=[],
        help="universe of surface tokens (e.g. git diff --name-only) for "
        "unexplored accounting; stored and merged across passes",
    )
    cp = sub.add_parser("check")
    cp.add_argument("--novelty-min", type=float, default=0.50)
    args = p.parse_args(argv)
    if args.branch is None or args.pass_n is None:
        sys.stderr.write("--branch and --pass are required\n")
        return 2
    if args.cmd == "record":
        return record(args)
    return check(args)


if __name__ == "__main__":
    sys.exit(main())
