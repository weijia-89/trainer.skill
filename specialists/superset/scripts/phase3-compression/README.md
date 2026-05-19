# Phase 3 compression infrastructure

Tools for the token-optimization-compression hybrid protocol with three-criterion fidelity.

## What this directory holds

| File | Role |
|---|---|
| `check-structural-preservation.py` | Criterion (a). Verifies every named structural element in the original SKILL.md survives in the compressed body. Headings, falsifiers (H1-Hn, M1-Mn, PV-1, S1), patterns (Pattern A-I), shapes (Shape A/B/C), workers (A1/A2/A3/A4a/...), explicit anchor-incidents, fixtures, and section-grep markers. Exits 0 on PASS; non-zero with JSON to stderr on missing elements. |
| `score-section-similarity.py` | Criterion (b) proxy. Splits both files at headings, computes per-section `difflib.SequenceMatcher.ratio()` between original and compressed. Reports per-section ratios and a flagged-section list (ratio < threshold). Threshold defaults to 0.65, configurable via `--threshold`. Stdlib-only; no external dependencies. |
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
