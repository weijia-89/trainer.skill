#!/usr/bin/env python3
"""score-section-similarity.py - Criterion (b) proxy for Phase 3 compression.

Splits both files at level-2 headings (## Section), computes per-section
difflib.SequenceMatcher.ratio() between original and compressed sections.
Reports per-section ratios + flagged-section list (ratio < threshold).

Stdlib-only; no external dependencies (no BERTScore, no sklearn).

Threshold semantics:
  ratio = 1.0: identical
  ratio >= 0.85: minor wording changes
  ratio >= 0.65 (default): substantive but recognizable; reasonable compression target
  ratio >= 0.40: heavy compression, semantic equivalence unclear
  ratio < 0.40: section likely lost or rewritten

Usage:
    python3 score-section-similarity.py <original> <compressed>
    python3 score-section-similarity.py <original> <compressed> --threshold 0.65
"""

import sys
import re
import json
import argparse
from pathlib import Path
from difflib import SequenceMatcher


def split_at_headings(text, level=2):
    """Split markdown text into (heading, body) chunks at the given heading level.

    Returns a list of (heading_text, section_body) tuples. The body of each section
    is everything from after the heading to the next heading at the same level (or end).
    """
    pattern = re.compile(rf'^(#{{{level}}}\s+.*?)$', re.MULTILINE)
    matches = list(pattern.finditer(text))
    chunks = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        chunks.append((heading, body))
    return chunks


def normalize_heading(h):
    """Normalize heading for matching across original and compressed (case-insensitive, trimmed)."""
    return re.sub(r'^#+\s*', '', h.strip()).lower()


def main():
    parser = argparse.ArgumentParser(description='Score per-section similarity between original and compressed SKILL.md')
    parser.add_argument('original', help='Path to original SKILL.md')
    parser.add_argument('compressed', help='Path to compressed draft')
    parser.add_argument('--threshold', type=float, default=0.65, help='Minimum acceptable per-section ratio (default 0.65)')
    parser.add_argument('--median-threshold', type=float, default=0.80, help='Required median ratio across all sections (default 0.80)')
    parser.add_argument('--level', type=int, default=2, help='Heading level to split at (default 2 = ##)')
    args = parser.parse_args()

    orig_path = Path(args.original).resolve()
    comp_path = Path(args.compressed).resolve()

    if not orig_path.exists():
        print(json.dumps({'error': 'file-not-found', 'path': str(orig_path)}), file=sys.stderr)
        sys.exit(2)
    if not comp_path.exists():
        print(json.dumps({'error': 'file-not-found', 'path': str(comp_path)}), file=sys.stderr)
        sys.exit(2)

    orig_chunks = split_at_headings(orig_path.read_text(), level=args.level)
    comp_chunks = split_at_headings(comp_path.read_text(), level=args.level)

    # Build heading-keyed maps
    orig_map = {normalize_heading(h): b for (h, b) in orig_chunks}
    comp_map = {normalize_heading(h): b for (h, b) in comp_chunks}

    ratios = []
    flagged = []

    for (heading, body) in orig_chunks:
        key = normalize_heading(heading)
        if key not in comp_map:
            flagged.append({
                'heading': heading,
                'ratio': 0.0,
                'reason': 'section-missing-from-compressed',
            })
            ratios.append(0.0)
            continue
        ratio = SequenceMatcher(None, body, comp_map[key]).ratio()
        ratios.append(ratio)
        if ratio < args.threshold:
            flagged.append({
                'heading': heading,
                'ratio': round(ratio, 3),
                'reason': f'below-threshold-{args.threshold}',
            })

    # Sections present in compressed but not original (additions)
    added = []
    for key, body in comp_map.items():
        if key not in orig_map:
            added.append(key)

    median = sorted(ratios)[len(ratios) // 2] if ratios else 1.0
    mean = sum(ratios) / len(ratios) if ratios else 1.0
    minimum = min(ratios) if ratios else 1.0

    print(f'SUMMARY  sections in original: {len(orig_chunks)}')
    print(f'SUMMARY  sections in compressed: {len(comp_chunks)}')
    print(f'SUMMARY  added in compressed (not in original): {len(added)}')
    print(f'SUMMARY  median ratio: {median:.3f}')
    print(f'SUMMARY  mean ratio: {mean:.3f}')
    print(f'SUMMARY  minimum ratio: {minimum:.3f}')

    for f in flagged:
        print(json.dumps(f), file=sys.stderr)

    floor_pass = minimum >= args.threshold
    median_pass = median >= args.median_threshold

    if not flagged and floor_pass and median_pass:
        print(f'PASS  all sections >= {args.threshold} floor; median {median:.3f} >= {args.median_threshold} threshold')
        sys.exit(0)

    if not floor_pass:
        print(f'FAIL  minimum ratio {minimum:.3f} < {args.threshold} floor ({len(flagged)} section(s) flagged)', file=sys.stderr)
        sys.exit(1)
    if not median_pass:
        print(f'FAIL  median ratio {median:.3f} < {args.median_threshold} threshold', file=sys.stderr)
        sys.exit(1)

    print(f'PASS  all sections >= {args.threshold}; median {median:.3f} >= {args.median_threshold}')
    sys.exit(0)


if __name__ == '__main__':
    main()
