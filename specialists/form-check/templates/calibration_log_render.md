---
name: calibration_log_render
version: 2.0.0
parent_skill: form-check
---

# Calibration Log — render template

The canonical log is JSONL at `.recovery/calibration.jsonl`. Render to markdown for human review using this template.

## Schema (per row)

```json
{
  "ts": "ISO-8601 UTC",
  "change_id": "PR-NNN or commit-sha or engagement-id",
  "tier": "vibe-dangerous | vibe-careful | vibe-safe | refactor",
  "score": 0,
  "components": {
    "code_read": 0,
    "test": 0,
    "hallucination": 0,
    "bug_class": 0,
    "adversarial": 0,
    "reversibility": 0,
    "doc": 0,
    "blast_radius": 0,
    "threat_model": 0
  },
  "shipped": true,
  "incident": null,
  "incident_ts": null,
  "incident_severity": null,
  "engagement_level": false
}
```

## Render command

```bash
# Quick render
jq -r '
  ["ts","change_id","tier","score","shipped","incident_severity"] as $cols
  | ($cols | @tsv),
    (. | [.ts, .change_id, .tier, .score, .shipped, .incident_severity // "-"] | @tsv)
' .recovery/calibration.jsonl | column -ts $'\t'
```

## Aggregation queries

### Tier-vs-incident-rate (after ≥50 entries per tier)

```bash
jq -s '
  group_by(.tier)
  | map({
      tier: .[0].tier,
      n: length,
      shipped: ([.[] | select(.shipped)] | length),
      incidents: ([.[] | select(.incident != null)] | length),
      mean_score: ([.[] | .score] | add / length),
      median_score: ([.[] | .score] | sort | .[length / 2 | floor])
    })
' .recovery/calibration.jsonl
```

### Component drift over time

```bash
jq -s '
  sort_by(.ts)
  | [.[].components.test]
' .recovery/calibration.jsonl
```

### Recent failures (score below tier-floor)

```bash
jq -r '
  select(.score < (
    if .tier == "vibe-dangerous" then 95
    elif .tier == "vibe-careful" then 90
    elif .tier == "vibe-safe" then 80
    else 70 end
  ))
  | [.ts, .change_id, .tier, .score] | @tsv
' .recovery/calibration.jsonl
```

## Markdown render (human review)

```markdown
# Calibration Log — {{project}}

> Last 30 days. Total scored changes: N. Tier breakdown: vibe-dangerous (X), vibe-careful (Y), vibe-safe (Z), refactor (W).

## Summary

| Tier | N | Mean score | Median score | Shipped | Incidents |
|---|---|---|---|---|---|
| vibe-dangerous | X | 95.2 | 96 | X-1 | 0 |
| vibe-careful | Y | 91.8 | 92 | Y | 1 |
| vibe-safe | Z | 84.5 | 85 | Z | 0 |
| refactor | W | 73.0 | 73 | W | 0 |

## Recent failures (below tier-floor)

| Date | Change | Tier | Score | Lowest component |
|---|---|---|---|---|
| 2026-05-12 | PR-184 | vibe-careful | 88 | test_verification (60) |

## Retier triggers

After ~50 entries per tier:
- If incident rate at score X is comparable to incident rate at threshold − 5: consider lowering the threshold by 2 points.
- If incident rate at threshold + 0–2 is significantly higher than threshold + 3+: consider raising the threshold.

Retier proposal goes through ADR review (no silent threshold changes).
```

## Anti-patterns

- Single-row log entries that drop the `components` breakdown — defeats the calibration purpose.
- Logging only successful scores — incident-correlated calibration requires logging *all* scores including the ones that failed the floor.
- "Forgot to log" — make logging part of the merge gate (CI fitness function: PR cannot merge without an entry referencing the PR ID for non-trivial changes).
- Rewriting historical entries — append-only.
