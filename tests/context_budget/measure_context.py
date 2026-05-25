#!/usr/bin/env python3
"""Report line/word/estimated-token counts for a markdown skill file."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def est_tokens(text: str) -> int:
    return (len(text) + 3) // 4


def section_stats(text: str) -> list[tuple[str, int, int, int]]:
    lines = text.splitlines()
    sections: list[tuple[str, int, int]] = []
    current = "(preamble)"
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if i > start:
                chunk = "\n".join(lines[start:i])
                sections.append((current, start + 1, i))
            current = line[3:].strip()
            start = i
    chunk = "\n".join(lines[start:])
    sections.append((current, start + 1, len(lines)))
    out: list[tuple[str, int, int, int]] = []
    for name, lo, hi in sections:
        body = "\n".join(lines[lo - 1 : hi])
        out.append((name, hi - lo + 1, len(body.split()), est_tokens(body)))
    return out


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "SKILL.md")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    words = len(re.findall(r"\S+", text))
    tokens = est_tokens(text)
    print(f"FILE={path}")
    print(f"LINES={len(lines)}")
    print(f"WORDS={words}")
    print(f"EST_TOKENS={tokens}")
    print("SECTIONS")
    stats = section_stats(text)
    for name, ln, wd, tok in sorted(stats, key=lambda x: x[3], reverse=True):
        print(f"  {name}\tlines={ln}\twords={wd}\test_tokens={tok}")
    print("TOP10_SECTIONS_BY_EST_TOKENS")
    for name, ln, wd, tok in sorted(stats, key=lambda x: x[3], reverse=True)[:10]:
        print(f"  {tok}\t{name}\t(lines={ln})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
