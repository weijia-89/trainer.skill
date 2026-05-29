# Trainer — executable contract surfaces

Canonical spec for **obligation B** during trainer-routed PR reviews. Composes with `trainer-codereview.md` step 3 and `form-check` COR.

## What counts as a contract surface

Declared places where the engagement repo tells agents or humans how to invoke shipped APIs:

- Skill trees (`SKILL.md`, bundled specialists, `.cursor/rules/*.mdc` that name runnable commands)
- Root agent contracts (`AGENTS.md`, `CLAUDE.md`)
- Workflow templates with copy-paste runnable snippets (CI job docs, `scripts/` README blocks cited as the operator path)

**Discover from the engagement repo.** Do not hard-code product repo paths inside `trainer.skill`.

## Export delta

A change that breaks or renames a **public** symbol consumers could rely on:

- Rename or remove exported function, class, CLI subcommand, config key, HTTP route, or documented script entrypoint
- Signature change (required args, return shape, error codes)
- Behavior change visible at the old call site without a compile error

No export delta → obligation B is **N/A** (A + C only).

## Obligations (A / B / C)

| ID | Name | Scope | When |
|----|------|-------|------|
| **A** | Diff-primary | Changed bodies + in-diff callers only | Always |
| **B** | Contract-closure | Find **OLD** name/signature in **declared contract surfaces only**; bounded grep/read | Export delta on this PR |
| **C** | Verify | Run repo verify/test if documented in Inputs Verify row (`trainer-codereview.md`); note if none | Always |

**Coexistence:** A is the default review boundary. B is an **exception carve-out** when export delta; it does not reopen full-repo review.

## APPROVE rules

- **A** satisfied (changed bodies + in-diff callers read for behavior PRs).
- If **export delta:** **B** satisfied **or** explicit waive row in **Bug inventory** with Status `waived`, reason, and **file list** of unchecked contract surfaces (severity per repo tier: toebeans P0–P3, buds P0–P4).
- **C:** verify command run and pass, or documented "no verify script" in review notes.

**Forbidden:** APPROVE on export delta without B closure and without a waive row naming every skipped surface.

## Bounds for B

- Search **declared surfaces only** (see above); no repo-wide symbol hunt.
- Stop when OLD symbol is absent from all declared surfaces, or each hit is updated/waived.
- Do not expand into unrelated refactors or undeclared markdown.

## Anti-patterns

- Treating "grep found nothing in diff" as B complete when export delta renamed a public API.
- Full-tree `rg` outside declared surfaces to satisfy B.
- Waiving B without listing which contract files were not checked.
- Duplicating Inputs Verify prose here; C defers to `trainer-codereview.md` Inputs table.

## Deprecation PRs

When the PR is a deprecate/sunset, also load `specialists/form-check/checklists/deprecation_policy.md` (timeline, headers, migration path).
