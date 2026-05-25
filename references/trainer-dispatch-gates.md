<!-- sdk-review F1: trainer-owned overlay; bundle rsync --delete removes specialists/ copies -->

# Trainer dispatch gates (superset cross-reference)

Root `trainer` fires dispatch discipline; `superset` owns worktrees, prompt templates, daily-log validation, and falsifier harnesses. Load `superset/SKILL.md` plus this file when multi-agent dispatch is in play.

## Trigger

Any phrase implying multi-agent dispatch: "spawn N agents", "run in parallel", "dispatch agents", "kick off a wave", "run these tasks today". Do not wait for an explicit manifest request.

## Action sequence

1. Auto-draft daily-log entries in `<project>/localonly/daily/<YYYY-MM-DD>.md` (create if absent). Each row: `name | role | owned_paths | depends_on | produces | consumes | phase | wall_clock | status`.
2. Self-adversarial review: run `superset` falsifier checklist plus `form-check` pass on the draft. Hunt owned-path overlaps, missing producer-consumer links, freeze-list violations, duplicate dispatches, same-tree cwd races.
3. Surface validated manifest and findings under **Decisions awaiting user sign-off** before per-agent prompts.

## Route-correction phrases

- "Just dispatch them, I'll review later."
- "Skip the manifest, it's only two agents."
- "Prompts can spot collisions on their own."
- "I'll figure out wave order as we go."
- "These are obviously independent."

## Anchor incidents

- Mailchimp 2026-05-18 duplicate dispatch: second agent wasted discovery on existing artifact.
- Buds 2026-05-19 parallel f-droid and LICENSE without `consumes` link: LICENSE agent lacked research output.

Coached override: two rounds max, then log.

## Three-layer architecture

| Layer | Lifespan | Role |
|-------|----------|------|
| Orch | ~1 day | Dispatches workers, coaches, writes daily log; handoff summary on rotation |
| Meta | ~1 week | Pattern extraction, meta-log; suggests, does not dispatch |
| Worker | Per task | Fresh-context agents under five-pillar prompt discipline |

Hand-off detail: `superset/SKILL.md` "Three-layer agent architecture". Trainer fires iron law; superset owns procedure.

## Status check + changelog/README

When operator refreshes status or closes the day: `superset` section **Status check + changelog/README iron law** and `templates/status-check-changelog.md`. Orch updates queue SSOT plus each touched repo `CHANGELOG.md` / `README.md`; chat points to SSOT only.
