#!/usr/bin/env python3
"""Verify every citation tag in skill content exists in references/notes.md OR in upstream REFERENCES.md.

Tag format: ALL-CAPS-WITH-NUMBERS-AND-DASHES, length ≥ 4, with at least one '-' separator.
Examples: METR-2025, OWASP-LLM-2025, SLOP-arXiv, CWE-25-2025.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Heuristic — match likely citation tags. Tighter than just \w+ to reduce false positives.
TAG_RE = re.compile(r"\b([A-Z][A-Z0-9]*-[A-Z0-9][A-Z0-9-]*)\b")

# Allowlisted strings that look like tags but aren't citations (e.g. acronym-shaped tokens
# used as ordinary terms in tables of contents, IDs, etc.).
ALLOWLIST = {
    "P0", "P1", "P2", "P3",  # severities
    "RPS", "TPS",             # rates
    "Q1", "Q2", "Q3", "Q4",  # quarters
    "PR-N",                  # placeholder
    "PR-NN", "PR-NNN",
    "INC-N",
    "PROMPT-MAJOR", "PROMPT-MINOR", "PROMPT-PATCH",
    "TODO", "FIXME", "XXX",
    "AC-X", "SC-Y", "SC-13", "SC-28",
    "AU", "RA", "IR", "CM", "SR",
    "CC1-CC9", "CC6.1", "CC6.7", "CC7.1", "CC7.2", "CC7.3", "CC8.1", "CC9.2",
    "A.5.15", "A.8.24", "A.8.15", "A.8.16", "A.8.8", "A.8.32",
    "A.5.24-5.30", "A.5.19-5.23",
    "ID-RA", "ID.RA-P3", "ID.RA-P4", "ID.RA-P5",  # NIST sub-categories
    "PDF-V4.2.0A", "FY26", "FY27",
    "MIT-VS-AGPL", "RR-LL",
    "L1", "L2", "L3", "L4",
    "API1", "API2", "API3", "API4", "API5", "API6", "API7", "API8", "API9", "API10",
    "LLM01", "LLM02", "LLM03", "LLM04", "LLM05", "LLM06", "LLM07", "LLM08", "LLM09", "LLM10",
    "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10",
    "API01", "API02",
    "RPO-RTO",
    "DEV-OPS",
    "M-N", "P-N",
    "PR-184",
    # Domain English used in SHOUTY Iron-Law text and CHANGELOG echo — not citations.
    "TIER-FLOOR", "PER-COMPONENT",
    # Frontier-model identifiers used as operational labels in audit prose
    # (Phase 11 manual audit, 2026-05-17). Not academic citations; the regex
    # is correct to flag them, the audit prose is correct to name them.
    "GPT-3", "GPT-4", "GPT-5", "GPT-4o", "GPT-4O",
    "CLAUDE-3", "CLAUDE-4", "OPUS-4",
    "GEMINI-1", "GEMINI-2",
    "LLAMA-3", "LLAMA-4",
}


SKIP_PREFIX = (
    "CWE-",            # CWE-79 etc. covered by CWE-25-2025
    "P0-", "P1-", "P2-", "P3-",  # finding IDs in templates
    "T-", "P-", "M-", "X-",      # generic placeholder IDs
    "API0", "API1",    # OWASP API sub-IDs
    "LLM0", "LLM1",    # OWASP LLM sub-IDs
    "A0", "A1",        # OWASP Web sub-IDs
    "OWASP-LLM", "OWASP-API",  # category labels and sub-IDs (e.g. OWASP-API-08)
    "STRIDE-", "LINDDUN-",       # threat-model categories
    "SHA-", "AES-",              # crypto primitives
    "ISO-",                      # date formats / ISO standards used inline
    "GPL-", "AGPL-", "BSD-",     # license identifiers
    "PR-", "ADR-", "AUD-", "INC-",  # generic ticket/PR/ADR/incident placeholders
    "AI-PR",                     # category label
    "C-FFI", "PCI-DSS",          # acronyms used as ordinary terms
    "YYYY-",                     # date placeholder
)

def collect_tags(content: str) -> set[str]:
    out: set[str] = set()
    for m in TAG_RE.finditer(content):
        tag = m.group(1)
        if tag in ALLOWLIST:
            continue
        if any(tag.startswith(p) for p in SKIP_PREFIX):
            continue
        out.add(tag)
    return out


def collect_known_tags(refs_files: list[Path]) -> set[str]:
    known: set[str] = set()
    for path in refs_files:
        if not path.exists():
            continue
        text = path.read_text()
        for m in TAG_RE.finditer(text):
            known.add(m.group(1))
    return known


def main() -> int:
    here = Path(__file__).resolve().parent
    skill = here.parent
    # The upstream development bundle has been archived in a private local-only
    # directory and is no longer maintained. The skill is now self-contained:
    # every tag used in skill content must be defined in this skill's
    # references/notes.md.
    refs_files = [
        skill / "references" / "notes.md",
    ]
    known = collect_known_tags(refs_files)

    fail = 0
    orphan_set: set[str] = set()
    for md in skill.rglob("*.md"):
        # Skip fixtures + bak + the references file itself
        if "tests/fixtures" in str(md) or ".bak" in str(md):
            continue
        if md.parent == skill / "references":
            continue
        used = collect_tags(md.read_text())
        for tag in used:
            if tag not in known:
                orphan_set.add(tag)

    if orphan_set:
        print("FAIL: orphan citation tags (not in references/notes.md or REFERENCES.md):", file=sys.stderr)
        for t in sorted(orphan_set):
            print(f"  - {t}", file=sys.stderr)
        fail = 1
    else:
        print(f"test_citations.py: PASS ({len(known)} tags known; 0 orphans)")
    return fail


if __name__ == "__main__":
    sys.exit(main())
