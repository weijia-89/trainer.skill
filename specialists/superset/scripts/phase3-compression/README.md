# Phase 3 compression infrastructure

Tools for the token-optimization-compression hybrid protocol with three-criterion fidelity.

## What this directory holds

| File | Role |
|---|---|
| `check-structural-preservation.py` | Criterion (a) for SKILL.md specifically. Hardcoded knowledge of SKILL.md vocabulary: falsifiers (H1-Hn, M1-Mn, PV-1, S1), patterns (Pattern A-I), shapes (Shape A/B/C), workers (A1/A2/A3/A4a/...), code fences, headings. Exits 0 on PASS; non-zero with JSON to stderr on missing elements. Used for v0.7.1 SKILL.md compression. |
| `check-agent-ingest-preservation.py` | Criterion (a) generic, for ANY agent-ingest markdown file (templates, references, schema docs). Stdlib-only; no PyYAML dep. Default extractors cover headings (per-level), code fences, YAML frontmatter keys, table rows, list items, backtick-wrapped paths, capitalized-IDs ([A-Z]{1,3}-?\d+). Optional `--config <path>` (JSON) declares per-file STOP zones: `verbatim_required` (exact strings), `custom_id_patterns` (regex+label), `placeholder_required` (count must not decrease), `anchor_phrases` (count must not decrease). Config-tracked elements are STRICT; default-tracked default to 95% threshold with `--strict` override. See `configs/` for examples. |
| `score-section-similarity.py` | Criterion (b) proxy. File-type-agnostic. Splits both files at headings (`--level` configurable, default 2), computes per-section `difflib.SequenceMatcher.ratio()` between original and compressed. Reports per-section ratios and a flagged-section list (ratio < threshold). Floor 0.65 (`--threshold`), median 0.80 (`--median-threshold`). Stdlib-only. Works for SKILL.md AND template/reference compression with no changes. |
| `configs/*.json` | Per-file STOP-zone configs for `check-agent-ingest-preservation.py`. Each config names the verbatim phrases, placeholder slots, custom IDs, and anchor citations that compression must preserve. Currently: `agent-prompt.json`. Add one per agent-ingest target as compression sessions kick off. |
| `behavioral-ab-spec.md` | Criterion (c). Specifies the asynchronous A/B test that validates behavioral equivalence between original and compressed SKILL.md. Includes dispatch protocol, measurement, equivalence criterion, fail-safe rollback. Designed for a fresh-context chat to execute. |

## Usage

Recommended sequence per compression iteration:

```bash
# 1. Author compressed draft (manual, in editor) at SKILL.md.compressed-draft
# 2. Run structural-preservation check
python3 scripts/phase3-compression/check-structural-preservation.py \
    SKILL.md SKILL.md.compressed-draft

# 3. Run similarity scoring
python3 scripts/phase3-compression/score-section-similarity.py \
    SKILL.md SKILL.md.compressed-draft \
    --threshold 0.65

# 4. If both pass, stage as SKILL.md.v0.7.1-draft and queue (c) A/B for fresh chat
# 5. After fresh chat runs (c), if equivalence holds: promote to SKILL.md, bump version, run verify_trainer_sync.sh
```

## Fidelity criterion design notes

**Three criteria are intentionally orthogonal** so they catch different failure modes:

- (a) catches structural-element drop (e.g., a falsifier-checklist row removed during compression)
- (b) catches semantic drift at section level (e.g., paragraph tightened to the point of changing meaning)
- (c) catches behavioral drift (e.g., compressed body produces subtly different agent dispatches than original)

A compression that passes (a) but fails (b) is over-tight. A compression that passes (a)+(b) but fails (c) is semantically equivalent but behaviorally different (a real failure mode for prompt-shaped documents that depend on cumulative-priming effects across the body).

The 98% fidelity target named in earlier roadmap docs is operationalized as: (a) 100% structural preservation, (b) section similarity >= 0.65 floor / 0.80 median, (c) A/B equivalence on >=2 task types in fresh chats. Numbers are speculative priors per Wei's deai calibration discipline; iterate after first run.

## Out of scope

- Token counting (use `tiktoken` or `wc -w` separately; the scripts here do not measure compression ratio directly because the operator should decide acceptable token reduction case-by-case)
- Automated compression (the scripts verify, they do not author)
- Visual diff (use `git diff --no-index` or `vimdiff` for human inspection)
