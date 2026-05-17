# warmup, front desk; tell me what's broken and I'll route you

A front-desk skill that routes you to the right downstream code skill when you do not yet know which one to invoke.

## What it does

You walked in. You have a coding question, problem, or project, and you do not know which of the eight skills in the ecosystem handles it. `warmup` reads your situation, points to the right skill, and gets out of the way.

Three things `warmup` does:

- Presents a routing table for eight situations a developer commonly faces.
- Tier-classifies the change (vibe-safe / vibe-careful / vibe-dangerous) when the answer is `form-check` or `recovery`.
- Surfaces the operationalized graduation checklist when you have been using the skill for a while.

Three things it does not do: score code, plan architecture, run engagements. Those belong to downstream skills. The front desk does not treat you; it triages.

## When to invoke

- You are new to this code-skill ecosystem and do not yet know which one to use.
- You have a situation that does not fit cleanly into one of the deeper skills.
- You want to confirm you are about to invoke the right thing.

## When to skip

- You already know which downstream skill applies. Go to it directly. `warmup` is a developer onboarding aid, not a permanent layer.
- Production is on fire. Go directly to `diet §3`. A routing table is the wrong artifact during an incident.

## Composes with

The skill routes to and references seven downstream skills:

- `program`, vague idea to scoped spec
- `form-check`, single-change review and planning
- `recovery`, multi-day full-project quality engagement
- `pr`, deploy mechanics
- `diet`, operate and incident response
- `safetybar`, git recovery
- `gymbuddy`. AI-assisted-development workflow

And references one cross-cutting checklist: `form-check/checklists/codebase_scan.md`.

## Outgrowing the skill

`warmup` is designed to be temporary. You should outgrow it within 5–10 invocations. The graduation signal is operationalized in `graduation_checklist.md`, a six-item self-assessment with concrete pass criteria. Run it once a month while you are still using the skill.

When you can answer all six items correctly on two consecutive monthly reviews, stop invoking `warmup` and route directly to downstream skills. You can leave the skill installed; the next person in your shared environment may not have graduated yet.

## Files

- `SKILL.md`, the routing table and the harness contract
- `graduation_checklist.md`, operationalized outgrow signal
- `CHANGELOG.md`, version history
- This file

## License

MIT.
