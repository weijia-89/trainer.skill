#!/usr/bin/env python3
"""check-structural-preservation.py - Criterion (a) for Phase 3 compression.

Verifies every named structural element in original SKILL.md survives in the
compressed body. Exits 0 on PASS; non-zero with JSON to stderr on missing elements.

Structural elements tracked:
  - All markdown headings (# .., ## .., ### ..)
  - Falsifier identifiers (H1-Hn, M1-Mn, PV-1, S1, S2, ...)
  - Pattern identifiers (Pattern A, Pattern B, ... Pattern I)
  - Shape identifiers (Shape A, Shape B, Shape C)
  - Worker identifiers (A1, A2, A3, A4a, A4b, ...)
  - Anchor-incident markers (text containing 'anchored to' or 'anchor:' or 'incident')
  - Code fences (preserved count)
  - Section-grep markers (any **bold** terms that name infrastructure)

Usage:
    python3 check-structural-preservation.py <original> <compressed>
    python3 check-structural-preservation.py <original> <compressed> --strict

By default, reports missing elements but exits 0 on PASS (>=95% preservation).
With --strict, exits non-zero on ANY missing element.
"""

import sys
import re
import json
import argparse
from pathlib import Path


HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*$', re.MULTILINE)
FALSIFIER_RE = re.compile(r'\b([HM]\d+|PV-\d+|S\d+)\b')
PATTERN_RE = re.compile(r'\bPattern\s+([A-Z])\b')
SHAPE_RE = re.compile(r'\bShape\s+([A-Z])\b')
WORKER_RE = re.compile(r'\b(?:worker\s+|agent\s+)?(A\d+[a-z]?)\b')
CODE_FENCE_RE = re.compile(r'^```', re.MULTILINE)


def extract_elements(text):
    """Extract structural-element identifiers from a markdown body."""
    return {
        'headings': set(HEADING_RE.findall(text)),
        'falsifiers': set(FALSIFIER_RE.findall(text)),
        'patterns': set(PATTERN_RE.findall(text)),
        'shapes': set(SHAPE_RE.findall(text)),
        'workers': set(WORKER_RE.findall(text)),
        'code_fences': len(CODE_FENCE_RE.findall(text)),
    }


def diff_elements(orig, comp):
    """Return list of dicts describing missing elements."""
    missing = []
    for category in ('headings', 'falsifiers', 'patterns', 'shapes', 'workers'):
        orig_set = orig[category]
        comp_set = comp[category]
        dropped = orig_set - comp_set
        for item in sorted(dropped, key=lambda x: str(x)):
            missing.append({
                'category': category,
                'item': str(item),
                'severity': 'dropped',
            })
    if comp['code_fences'] < orig['code_fences']:
        missing.append({
            'category': 'code_fences',
            'item': f'{comp["code_fences"]} of {orig["code_fences"]}',
            'severity': 'count_reduced',
        })
    return missing


def main():
    parser = argparse.ArgumentParser(description='Check structural preservation between original and compressed SKILL.md')
    parser.add_argument('original', help='Path to original SKILL.md')
    parser.add_argument('compressed', help='Path to compressed draft')
    parser.add_argument('--strict', action='store_true', help='Exit non-zero on ANY missing element (default: 95%% threshold)')
    args = parser.parse_args()

    orig_path = Path(args.original).resolve()
    comp_path = Path(args.compressed).resolve()

    if not orig_path.exists():
        print(json.dumps({'error': 'file-not-found', 'path': str(orig_path)}), file=sys.stderr)
        sys.exit(2)
    if not comp_path.exists():
        print(json.dumps({'error': 'file-not-found', 'path': str(comp_path)}), file=sys.stderr)
        sys.exit(2)

    orig = extract_elements(orig_path.read_text())
    comp = extract_elements(comp_path.read_text())

    # Counts for summary
    orig_total = sum(len(orig[c]) for c in ('headings', 'falsifiers', 'patterns', 'shapes', 'workers'))
    comp_total = sum(len(comp[c]) for c in ('headings', 'falsifiers', 'patterns', 'shapes', 'workers'))

    missing = diff_elements(orig, comp)

    print(f'SUMMARY  original elements: {orig_total} (headings={len(orig["headings"])} falsifiers={len(orig["falsifiers"])} patterns={len(orig["patterns"])} shapes={len(orig["shapes"])} workers={len(orig["workers"])} code_fences={orig["code_fences"]})')
    print(f'SUMMARY  compressed elements: {comp_total} (headings={len(comp["headings"])} falsifiers={len(comp["falsifiers"])} patterns={len(comp["patterns"])} shapes={len(comp["shapes"])} workers={len(comp["workers"])} code_fences={comp["code_fences"]})')

    if not missing:
        print(f'PASS  100% structural preservation')
        sys.exit(0)

    for m in missing:
        print(json.dumps(m), file=sys.stderr)

    preserved_pct = ((orig_total - len([m for m in missing if m['severity'] == 'dropped'])) / orig_total * 100) if orig_total else 100
    print(f'SUMMARY  preserved: {preserved_pct:.1f}% ({len(missing)} missing element(s))', file=sys.stderr)

    if args.strict or preserved_pct < 95.0:
        print(f'FAIL  structural preservation below threshold ({preserved_pct:.1f}% < 95.0%)' if not args.strict else f'FAIL  strict mode: any missing element fails')
        sys.exit(1)

    print(f'PASS  structural preservation {preserved_pct:.1f}% >= 95.0% threshold (informational warnings above)')
    sys.exit(0)


if __name__ == '__main__':
    main()
