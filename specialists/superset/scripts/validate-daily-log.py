#!/usr/bin/env python3
"""validate-daily-log.py - Validates a daily-log manifest against superset v0.7.0 constraints.

Usage: python3 validate-daily-log.py <path-to-daily-log.md> [--project-root <path>]

Exits 0 on PASS (with warnings to stderr); non-zero on FAIL with structured-error JSON to stderr.

Hard falsifiers (FAIL):
  H11: owned_paths non-overlap within a phase
  H13: phase field stated for every agent
  H14: artifact-existence pre-dispatch (skipped if retro_authored: true in frontmatter)
  H15: producer-consumer chain (consumed path is produced by earlier-phase agent OR exists in live project tree)
  DAG: phase + depends_on forms a DAG (no cycles)
  Freeze: owned_paths intersecting high-stakes-list.yaml requires precondition

Soft warnings (PASS but flagged on stderr):
  PV-1: owned_paths existence in live project tree (Q02 path-verify, added v0.7.0)
  S1:  signals field present on every agent row (Q01 typed-signals, added v0.7.0)

v0.7.0 additions:
  - retro_authored: true frontmatter key skips H14 (Q03, added v0.7.0)
  - H15 accepts live-tree-existing consumed paths (collateral fix during retro validation)
  - PV-1 soft warning surfaces dispatch-time vs action-time path drift (Q02)
  - S1 soft warning prompts orchestrators to declare typed signals or explicit empty (Q01)

Uses a stdlib-only YAML subset parser tuned to the daily-log manifest shape.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path


# ---------- minimal YAML subset parser ----------

def parse_yaml_subset(text):
    """Parse a constrained YAML subset.

    Supports:
      - Top-level scalars: `key: value` (str, int, bool)
      - Inline empty list: `key: []`
      - Block scalars under indented key
      - List of dicts: `agents:` followed by indented `- name: x` blocks
      - List of scalars: `owned_paths:` followed by indented `- path` lines

    Returns a dict.
    """
    lines = [ln for ln in text.split('\n') if ln.strip() and not ln.lstrip().startswith('#')]
    return _parse_block(lines, 0, 0)[0]


def _parse_value(raw):
    """Coerce a raw YAML scalar to Python."""
    s = raw.strip()
    if s == '' or s.lower() in ('null', '~'):
        return None
    if s == '[]':
        return []
    if s == '{}':
        return {}
    if s.lower() == 'true':
        return True
    if s.lower() == 'false':
        return False
    # Strip surrounding quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def _indent(line):
    return len(line) - len(line.lstrip())


def _parse_block(lines, start, expected_indent):
    """Parse a block at the given indent level. Returns (dict, end_index)."""
    result = {}
    i = start
    while i < len(lines):
        line = lines[i]
        ind = _indent(line)
        if ind < expected_indent:
            return result, i
        if ind > expected_indent:
            # Unexpected deeper indent at the start of a block; skip
            i += 1
            continue
        stripped = line.strip()
        if ':' not in stripped:
            return result, i
        key, _, raw_value = stripped.partition(':')
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            result[key] = _parse_value(raw_value)
            i += 1
        else:
            # Block-value follows: list-of-dicts, list-of-scalars, or sub-dict
            next_i = i + 1
            if next_i >= len(lines):
                result[key] = None
                return result, next_i
            next_line = lines[next_i]
            next_ind = _indent(next_line)
            if next_ind <= expected_indent:
                # Empty block
                result[key] = None
                i = next_i
                continue
            if next_line.strip().startswith('- '):
                # List
                items, end = _parse_list(lines, next_i, next_ind)
                result[key] = items
                i = end
            else:
                # Sub-dict
                sub, end = _parse_block(lines, next_i, next_ind)
                result[key] = sub
                i = end
    return result, i


def _parse_list(lines, start, expected_indent):
    """Parse a list at the given indent. Returns (list, end_index)."""
    items = []
    i = start
    while i < len(lines):
        line = lines[i]
        ind = _indent(line)
        if ind < expected_indent:
            return items, i
        stripped = line.strip()
        if not stripped.startswith('- '):
            return items, i
        # The item content
        content = stripped[2:].strip()
        if ':' in content and not content.startswith('"'):
            # Item is a dict; parse it as a sub-block where the first key starts at this line
            # Re-construct lines so the first key is at expected_indent + 2
            first_key_line = (' ' * (expected_indent + 2)) + content
            # Find the extent of this item
            item_end = i + 1
            while item_end < len(lines) and _indent(lines[item_end]) > expected_indent:
                item_end += 1
            sub_lines = [first_key_line] + lines[i + 1:item_end]
            item_dict, _ = _parse_block(sub_lines, 0, expected_indent + 2)
            items.append(item_dict)
            i = item_end
        else:
            # Item is a scalar
            items.append(_parse_value(content))
            i += 1
    return items, i


def parse_frontmatter(text):
    """Extract YAML front-matter (between two `---` lines) and parse it."""
    match = re.search(r'^---\s*\n(.*?)\n---\s*$', text, re.DOTALL | re.MULTILINE)
    if not match:
        # Some daily logs have front-matter starting at line 1 with first `---`
        match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not match:
        raise ValueError("No YAML front-matter delimited by `---` lines found")
    return parse_yaml_subset(match.group(1))


# ---------- validation ----------


def path_matches(owned_path, frozen_glob):
    """Match owned_path against a freeze-list glob (supports trailing /** and exact)."""
    if frozen_glob == owned_path:
        return True
    if frozen_glob.endswith('/**'):
        prefix = frozen_glob[:-3]
        return owned_path.startswith(prefix + '/') or owned_path == prefix
    if frozen_glob.endswith('/*'):
        prefix = frozen_glob[:-2]
        if not owned_path.startswith(prefix + '/'):
            return False
        rest = owned_path[len(prefix) + 1:]
        return '/' not in rest
    return False


def validate(manifest, daily_log_path, project_root):
    """Run all checks. Returns tuple (errors, warnings) of dict lists.

    errors block validation (non-zero exit). warnings are informational (PASS exit with stderr).
    """
    errors = []
    warnings = []
    agents = manifest.get('agents', []) or []
    is_retro = manifest.get('retro_authored') is True

    # Pre-condition: agents must be a list of dicts
    if not isinstance(agents, list):
        errors.append({'falsifier': 'schema', 'message': '`agents` must be a list'})
        return errors, warnings

    # Build phase map
    by_phase = {}
    for agent in agents:
        if not isinstance(agent, dict):
            errors.append({'falsifier': 'schema', 'agent': str(agent), 'message': 'Agent entry is not a dict'})
            continue
        phase = agent.get('phase')
        if phase is None:
            errors.append({
                'falsifier': 'H13',
                'agent': agent.get('name', '?'),
                'message': f'Agent {agent.get("name", "?")} missing required `phase` field',
            })
            continue
        by_phase.setdefault(phase, []).append(agent)

    # H11: owned_paths non-overlap WITHIN a phase
    for phase, phase_agents in by_phase.items():
        seen = {}
        for agent in phase_agents:
            for path in (agent.get('owned_paths') or []):
                if path in seen and seen[path] != agent.get('name'):
                    errors.append({
                        'falsifier': 'H11',
                        'agent': agent.get('name'),
                        'conflict_with': seen[path],
                        'path': path,
                        'phase': phase,
                        'message': f'Phase {phase}: agents `{agent.get("name")}` and `{seen[path]}` both claim owned_path `{path}`',
                    })
                else:
                    seen[path] = agent.get('name')

    # H15: producer-consumer chain (every consumes has matching produces in earlier phase)
    produces_map = {}  # produces_path -> list of (agent_name, phase)
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        agent_phase = agent.get('phase', 0)
        for produced in (agent.get('produces') or []):
            produces_map.setdefault(produced, []).append((agent.get('name'), agent_phase))

    for agent in agents:
        if not isinstance(agent, dict):
            continue
        agent_phase = agent.get('phase', 0)
        for consumed in (agent.get('consumes') or []):
            producers = produces_map.get(consumed, [])
            earlier = [p for p in producers if p[1] < agent_phase]
            if not earlier:
                # v0.7.0 H15 fix: live-tree fallback. If the consumed path exists
                # in the project at validation time, the consumer can read it
                # directly without an earlier-phase batch producer. Useful for
                # both retro manifests and any batch consuming pre-existing
                # project state.
                live_full = project_root / consumed
                if live_full.exists():
                    continue
                errors.append({
                    'falsifier': 'H15',
                    'agent': agent.get('name'),
                    'consumes': consumed,
                    'agent_phase': agent_phase,
                    'message': f'Agent `{agent.get("name")}` (phase {agent_phase}) consumes `{consumed}` but no earlier-phase agent produces it and the path does not exist in the live project tree',
                })

    # DAG acyclicity (via depends_on)
    graph = {a.get('name'): list(a.get('depends_on') or []) for a in agents if isinstance(a, dict)}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}

    def has_cycle(node):
        color[node] = GRAY
        for nbr in graph.get(node, []):
            if nbr not in color:
                continue
            if color[nbr] == GRAY:
                return True
            if color[nbr] == WHITE and has_cycle(nbr):
                return True
        color[node] = BLACK
        return False

    for n in list(graph.keys()):
        if color[n] == WHITE and has_cycle(n):
            errors.append({
                'falsifier': 'DAG',
                'message': f'depends_on graph contains a cycle reachable from `{n}`',
            })
            break

    # H14: artifact-existence pre-dispatch (skipped on retro manifests per Q03 v0.7.0)
    if not is_retro:
        for agent in agents:
            if not isinstance(agent, dict):
                continue
            for produced in (agent.get('produces') or []):
                full = project_root / produced
                if full.exists():
                    errors.append({
                        'falsifier': 'H14',
                        'agent': agent.get('name'),
                        'produces': produced,
                        'resolved_path': str(full),
                        'message': f'Agent `{agent.get("name")}` would produce `{produced}` but that file already exists. Halt and confirm overwrite vs v2 vs skip.',
                    })

    # Freeze-list intersection
    freeze_list_path = project_root / 'localonly' / 'daily' / 'high-stakes-list.yaml'
    if freeze_list_path.exists():
        try:
            freeze_text = freeze_list_path.read_text()
            freeze_doc = parse_yaml_subset(freeze_text)
            freeze = (freeze_doc.get('freeze') or {})
        except Exception as e:
            freeze = {}
            errors.append({
                'falsifier': 'freeze-list-parse',
                'message': f'Failed to parse high-stakes-list.yaml: {e}',
            })
        if isinstance(freeze, dict):
            for agent in agents:
                if not isinstance(agent, dict):
                    continue
                precondition = agent.get('precondition')
                for owned_path in (agent.get('owned_paths') or []):
                    for frozen in freeze.keys():
                        if path_matches(owned_path, frozen):
                            if not precondition:
                                errors.append({
                                    'falsifier': 'freeze-list',
                                    'agent': agent.get('name'),
                                    'owned_path': owned_path,
                                    'frozen_path': frozen,
                                    'message': f'Agent `{agent.get("name")}` owns frozen path `{owned_path}` matching `{frozen}` but has no precondition declared',
                                })

    # PV-1 soft warning (Q02 v0.7.0): owned_paths existence in live project tree.
    # Surfaces dispatch-time vs action-time path drift. Glob patterns are checked
    # for at-least-one match; literal paths are checked for existence. Warning only,
    # not a fail, because owned_paths legitimately include not-yet-created files for
    # forward batches.
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        for path in (agent.get('owned_paths') or []):
            if any(ch in path for ch in '*?['):
                matches = list(project_root.glob(path))
                if not matches:
                    warnings.append({
                        'warning': 'PV-1',
                        'agent': agent.get('name'),
                        'owned_path': path,
                        'message': f'Agent `{agent.get("name")}` glob owned_path `{path}` matches zero files in project tree (verify path correctness before dispatch)',
                    })
            else:
                full = project_root / path
                if not full.exists():
                    warnings.append({
                        'warning': 'PV-1',
                        'agent': agent.get('name'),
                        'owned_path': path,
                        'message': f'Agent `{agent.get("name")}` owned_path `{path}` does not exist in project tree (legitimate for new-file creation; verify if path was intended to reference an existing file)',
                    })

    # S1 soft warning (Q01 v0.7.0): typed signals field presence on each agent row.
    # Prompts orchestrators to either populate signals: [...] with typed non-commit
    # entries or explicitly declare signals: [] to opt out. Catches the per-commit
    # ledger blind spot where violations, no-ops, and retrospectives drop on the floor.
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        if 'signals' not in agent:
            warnings.append({
                'warning': 'S1',
                'agent': agent.get('name'),
                'message': f'Agent `{agent.get("name")}` row has no `signals` key. Add signals: [] to declare explicit empty, or signals: [{{kind: ..., description: ...}}] for violations/no-ops/retrospectives that did not result in a commit.',
            })

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description='Validate a daily-log manifest against superset v0.4.0 constraints.')
    parser.add_argument('daily_log', help='Path to daily-log .md file')
    parser.add_argument('--project-root', default=None, help='Project root for artifact-existence checks (defaults to two parents up from daily_log)')
    args = parser.parse_args()

    path = Path(args.daily_log).resolve()
    if not path.exists():
        print(json.dumps({'error': 'file-not-found', 'path': str(path)}), file=sys.stderr)
        sys.exit(2)

    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        # daily_log is at <project_root>/localonly/daily/<file>.md
        project_root = path.parent.parent.parent

    text = path.read_text()
    try:
        manifest = parse_frontmatter(text)
    except ValueError as e:
        print(json.dumps({'falsifier': 'H15', 'error': 'frontmatter-parse-fail', 'message': str(e)}), file=sys.stderr)
        sys.exit(1)

    errors, warnings = validate(manifest, path, project_root)
    for w in warnings:
        print(json.dumps(w), file=sys.stderr)
    if errors:
        for e in errors:
            print(json.dumps(e), file=sys.stderr)
        print(f'FAIL  {len(errors)} validation error(s) for {path} ({len(warnings)} warning(s) above)', file=sys.stderr)
        sys.exit(1)

    if warnings:
        print(f'PASS  {path} validated against superset v0.7.0 constraints with {len(warnings)} warning(s) (project_root={project_root})')
    else:
        print(f'PASS  {path} validated against superset v0.7.0 constraints (project_root={project_root})')
    sys.exit(0)


if __name__ == '__main__':
    main()
