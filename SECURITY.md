# Security policy for trainer.skill

## Scope

This repository distributes the `trainer` entrypoint skill and nine bundled specialist skills as Markdown documentation. Nothing here runs as a service, opens network ports, or processes user data at runtime. Agents and humans read these files locally in an IDE or skill directory.

## What we cover

- Malicious or misleading content in shipped skill Markdown (prompt injection in templates, credential placeholders committed as live secrets).
- Supply-chain issues in repository scripts under `scripts/` (for example `bundle_specialists.sh`, `verify_trainer_sync.sh`, `apply_branch_protection.sh`).
- Incorrect security guidance in user-facing docs that could cause harm if followed.

## Out of scope

- How you configure your agent, IDE, or local skill mirrors. That is your environment.
- Runtime behavior of bundled specialist tools when you invoke them in your own projects.
- Issues in sibling canonical repos at `~/Projects/<name>.skill/` unless the same flaw exists in this bundle and you can reproduce from a clone of **this** repo.

## Supported versions

| Version | Status | Notes |
| ------- | ------ | ----- |
| 0.10.x | supported | Current line; see `CHANGELOG.md` |
| 0.9.x | security-only | Critical doc or script fixes at maintainer discretion |
| < 0.9 | unsupported | Upgrade recommended |

We tag releases on GitHub when the maintainer cuts a version. The `SKILL.md` frontmatter `version` field tracks trainer skill SemVer.

## Reporting a vulnerability

**Do not** open public GitHub issues for security vulnerabilities.

Use [GitHub Security Advisories](https://github.com/weijia-89/trainer.skill/security/advisories/new) on this repo, or contact the repository owner privately.

Include:

- Affected file path(s) and commit hash if known
- Steps to reproduce from a clean clone
- Impact (for example credential exposure or misleading auth guidance)

We aim to acknowledge within a few business days. We credit reporters on the advisory unless they request anonymity.

## No secrets in public issues

Do not paste API keys, tokens, private paths, or customer data into issues or PR comments. Use the private advisory flow above for anything sensitive.

## Secrets in skill content

Skill Markdown often lands in agent context. Do not commit live credentials to this repo. If you find a leaked secret in history, report it privately; do not post the secret in a public ticket.

## Branch protection

See `docs/BRANCH_PROTECTION.md` and `scripts/apply_branch_protection.sh`. Force-push and branch deletion on `main` are blocked for normal pushes once protection is applied; repo admins can bypass unless `enforce_admins` is enabled (see policy table in the branch-protection doc).

Owner: repo maintainers. Last reviewed: 2026-05-25.
