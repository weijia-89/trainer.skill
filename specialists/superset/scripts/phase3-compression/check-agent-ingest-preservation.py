#!/usr/bin/env python3
"""check-agent-ingest-preservation.py - Generic criterion (a) for any agent-ingest markdown file.

Verifies structural elements survive compression. File-type-agnostic; works on
templates, references, schema docs, agent-ingest prompt bodies, and any other
markdown file an AI agent reads or writes through.

Optional JSON config (--config <path>) for per-file STOP zones:
  - verbatim_required: list of exact strings that must appear at least once
  - custom_id_patterns: list of {regex, label} for file-specific ID families
  - placeholder_required: list of regex patterns whose count must not decrease
  - anchor_phrases: list of regex patterns for anchor-incident citations

Default elements tracked (no config required):
  - Markdown headings (all levels; reported per-level)
  - Code fences (count)
  - YAML frontmatter top-level keys (set)
  - Markdown table rows (count)
  - Top-level list items (count)
  - Backtick-wrapped paths (set)
  - Generic capitalized-IDs ([A-Z]{1,3}-?\\d+[a-z]?, e.g. H1, HO9, PV-1, A4a)

Stdlib-only; no PyYAML or other external deps.

Usage:
    python3 check-agent-ingest-preservation.py <original> <compressed>
    python3 check-agent-ingest-preservation.py <original> <compressed> --config configs/agent-prompt.json
    python3 check-agent-ingest-preservation.py <original> <compressed> --strict

Exit codes:
    0 PASS (default-tracked >=95% preserved; all config-tracked elements present)
    1 FAIL (any config-tracked element missing, OR default-tracked <95% without --strict)
    2 input error (file not found, malformed config)
"""

import sys
import re
import json
import argparse
from pathlib import Path

# Default extractors (file-type-agnostic)
HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*$', re.MULTILINE)
CODE_FENCE_RE = re.compile(r'^```', re.MULTILINE)
FRONTMATTER_RE = re.compile(r'\A---\n(.*?)\n---\n', re.DOTALL)
TABLE_ROW_RE = re.compile(r'^\|.*\|\s*$', re.MULTILINE)
TOP_LIST_RE = re.compile(r'^(?:- |\d+\.\s+)', re.MULTILINE)
PATH_BACKTICK_RE = re.compile(r'`([~/][^`]+|[\w./-]+\.[a-zA-Z0-9]+|\.{1,2}/[^`]+)`')
GENERIC_ID_RE = re.compile(r'\b([A-Z]{1,3}-?\d+[a-z]?)\b')


def extract_default_elements(text):
    """Extract file-type-agnostic structural elements."""
    headings_raw = HEADING_RE.findall(text)
    heading_by_level = {}
    for level_str, title in headings_raw:
        level = len(level_str)
        heading_by_level.setdefault(level, set()).add(title)

    fm_match = FRONTMATTER_RE.search(text)
    frontmatter_keys = set()
    if fm_match:
        for line in fm_match.group(1).split('\n'):
            m = re.match(r'^([a-zA-Z_][\w-]*)\s*:', line)
            if m:
                frontmatter_keys.add(m.group(1))

    return {
        'headings_by_level': heading_by_level,
        'headings_total': len(headings_raw),
        'code_fences': len(CODE_FENCE_RE.findall(text)),
        'frontmatter_keys': frontmatter_keys,
        'table_rows': len(TABLE_ROW_RE.findall(text)),
        'list_items': len(TOP_LIST_RE.findall(text)),
        'paths': set(PATH_BACKTICK_RE.findall(text)),
        'ids': set(GENERIC_ID_RE.findall(text)),
    }


def load_config(path):
    """Load JSON config; raise on malformed."""
    return json.loads(Path(path).read_text())


def extract_config_elements(text, config):
    """Extract per-file STOP-zone elements named in the config."""
    return {
        'verbatim_required': {
            phrase: text.count(phrase)
            for phrase in config.get('verbatim_required', [])
        },
        'custom_ids': {
            entry.get('label', entry['regex']): set(re.findall(entry['regex'], text))
            for entry in config.get('custom_id_patterns', [])
        },
        'placeholders': {
            pattern: len(re.findall(pattern, text))
            for pattern in config.get('placeholder_required', [])
        },
        'anchors': {
            pattern: len(re.findall(pattern, text))
            for pattern in config.get('anchor_phrases', [])
        },
    }


def diff_default_elements(orig, comp):
    """Return missing-element dicts for default-tracked categories."""
    missing = []
    for level, orig_titles in orig['headings_by_level'].items():
        comp_titles = comp['headings_by_level'].get(level, set())
        for title in sorted(orig_titles - comp_titles):
            missing.append({'category': f'heading_l{level}', 'item': title, 'severity': 'dropped'})
    if comp['code_fences'] < orig['code_fences']:
        missing.append({'category': 'code_fences', 'item': f'{comp["code_fences"]} of {orig["code_fences"]}', 'severity': 'count_reduced'})
    for key in sorted(orig['frontmatter_keys'] - comp['frontmatter_keys']):
        missing.append({'category': 'frontmatter_keys', 'item': key, 'severity': 'dropped'})
    if comp['table_rows'] < orig['table_rows']:
        missing.append({'category': 'table_rows', 'item': f'{comp["table_rows"]} of {orig["table_rows"]}', 'severity': 'count_reduced'})
    for id_ in sorted(orig['ids'] - comp['ids']):
        missing.append({'category': 'generic_ids', 'item': id_, 'severity': 'dropped'})
    for path in sorted(orig['paths'] - comp['paths']):
        missing.append({'category': 'paths', 'item': path, 'severity': 'dropped'})
    return missing


def diff_config_elements(orig_cfg, comp_cfg):
    """Return missing-element dicts for config-tracked categories. All STRICT (no threshold)."""
    missing = []
    for phrase, orig_count in orig_cfg['verbatim_required'].items():
        if orig_count > 0 and comp_cfg['verbatim_required'].get(phrase, 0) == 0:
            missing.append({'category': 'verbatim_required', 'item': phrase, 'severity': 'dropped'})
    for label, orig_set in orig_cfg['custom_ids'].items():
        comp_set = comp_cfg['custom_ids'].get(label, set())
        for id_ in sorted(orig_set - comp_set):
            missing.append({'category': f'custom_ids/{label}', 'item': id_, 'severity': 'dropped'})
    for pattern, orig_count in orig_cfg['placeholders'].items():
        comp_count = comp_cfg['placeholders'].get(pattern, 0)
        if comp_count < orig_count:
            missing.append({'category': 'placeholders', 'item': f'{pattern}: {comp_count} of {orig_count}', 'severity': 'count_reduced'})
    for pattern, orig_count in orig_cfg['anchors'].items():
        comp_count = comp_cfg['anchors'].get(pattern, 0)
        if comp_count < orig_count:
            missing.append({'category': 'anchors', 'item': f'{pattern}: {comp_count} of {orig_count}', 'severity': 'count_reduced'})
    return missing


def main():
    parser = argparse.ArgumentParser(description='Generic structural-preservation check for agent-ingest markdown files')
    parser.add_argument('original', help='Path to original file')
    parser.add_argument('compressed', help='Path to compressed file')
    parser.add_argument('--config', help='Optional JSON config with per-file STOP zones')
    parser.add_argument('--strict', action='store_true', help='Exit non-zero on ANY missing default-tracked element (default: 95%% threshold)')
    args = parser.parse_args()

    orig_path = Path(args.original).resolve()
    comp_path = Path(args.compressed).resolve()

    if not orig_path.exists():
        print(json.dumps({'error': 'file-not-found', 'path': str(orig_path)}), file=sys.stderr)
        sys.exit(2)
    if not comp_path.exists():
        print(json.dumps({'error': 'file-not-found', 'path': str(comp_path)}), file=sys.stderr)
        sys.exit(2)

    orig_text = orig_path.read_text()
    comp_text = comp_path.read_text()

    orig_elements = extract_default_elements(orig_text)
    comp_elements = extract_default_elements(comp_text)
    default_missing = diff_default_elements(orig_elements, comp_elements)

    print(f'SUMMARY  original: headings={orig_elements["headings_total"]} code_fences={orig_elements["code_fences"]} fm_keys={len(orig_elements["frontmatter_keys"])} table_rows={orig_elements["table_rows"]} list_items={orig_elements["list_items"]} paths={len(orig_elements["paths"])} ids={len(orig_elements["ids"])}')
    print(f'SUMMARY  compressed: headings={comp_elements["headings_total"]} code_fences={comp_elements["code_fences"]} fm_keys={len(comp_elements["frontmatter_keys"])} table_rows={comp_elements["table_rows"]} list_items={comp_elements["list_items"]} paths={len(comp_elements["paths"])} ids={len(comp_elements["ids"])}')

    config_missing = []
    if args.config:
        try:
            config = load_config(args.config)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(json.dumps({'error': 'config-load-failed', 'path': args.config, 'detail': str(e)}), file=sys.stderr)
            sys.exit(2)
        orig_cfg = extract_config_elements(orig_text, config)
        comp_cfg = extract_config_elements(comp_text, config)
        config_missing = diff_config_elements(orig_cfg, comp_cfg)
        print(f'SUMMARY  config: verbatim={len(orig_cfg["verbatim_required"])} custom_id_categories={len(orig_cfg["custom_ids"])} placeholders={len(orig_cfg["placeholders"])} anchors={len(orig_cfg["anchors"])}')

    all_missing = default_missing + config_missing

    if not all_missing:
        print('PASS  100% structural preservation (default + config)')
        sys.exit(0)

    for m in all_missing:
        print(json.dumps(m), file=sys.stderr)

    if config_missing:
        print(f'FAIL  {len(config_missing)} config-tracked element(s) missing (STOP-zone violation)')
        sys.exit(1)

    orig_default_total = (
        orig_elements['headings_total']
        + len(orig_elements['frontmatter_keys'])
        + len(orig_elements['ids'])
        + len(orig_elements['paths'])
    )
    dropped_count = len([m for m in default_missing if m['severity'] == 'dropped'])
    preserved_pct = ((orig_default_total - dropped_count) / orig_default_total * 100) if orig_default_total else 100.0

    if args.strict or preserved_pct < 95.0:
        msg = 'strict mode: any missing default-tracked element fails' if args.strict else f'default-tracked preservation {preserved_pct:.1f}% < 95.0% threshold'
        print(f'FAIL  {msg}')
        sys.exit(1)

    print(f'PASS  default-tracked preservation {preserved_pct:.1f}% >= 95.0%; config-tracked all preserved')
    sys.exit(0)


if __name__ == '__main__':
    main()
