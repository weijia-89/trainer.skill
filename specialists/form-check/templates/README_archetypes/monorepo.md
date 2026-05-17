---
name: README_monorepo_archetype
version: 2.0.0
parent_skill: form-check
voice: navigation-led; brief per-package context
---

# README archetype: Monorepo

```markdown
# {{org / monorepo-name}}

> What lives in this monorepo. ≤2 sentences. Why a monorepo (cite ADR if non-obvious).

## Structure

```
.
├── apps/                # deployable apps (one per directory)
│   ├── web/             # public web app (Next.js)
│   ├── api/             # public HTTP API (FastAPI)
│   └── admin/           # internal admin dashboard
├── packages/            # shared libraries (Python + TS)
│   ├── shared-types/    # cross-language schema contracts
│   ├── auth/
│   └── ui-components/
├── tools/               # repo-level tooling
├── docs/                # cross-cutting docs (per-app docs live in apps/<x>/docs/)
└── infrastructure/      # IaC for deployment
```

## Per-app readmes

Each app has its own README; this top-level README covers the *monorepo-level* concerns.

| App | Purpose | README |
|---|---|---|
| `apps/web` | Public web app | [README](apps/web/README.md) |
| `apps/api` | Public HTTP API | [README](apps/api/README.md) |
| `apps/admin` | Internal admin | [README](apps/admin/README.md) |

## Tooling

- **Build orchestrator**: {{Turborepo / Nx / pnpm workspaces / Bazel / Pants / Gradle composite}}
- **Languages**: {{Python {{ver}}, TypeScript {{ver}}, ...}}
- **Package manager**: {{pnpm + uv + ...}}
- **CI**: {{GitHub Actions; matrix per language}}
- **Test orchestrator**: per-language test runner; aggregated by tooling above

## Local development

### Prerequisites

- {{toolchain versions}} (managed via {{asdf / mise / Volta}})
- Docker

### One-time setup

```bash
make bootstrap
```

### Running an app

```bash
make dev APP=web
make dev APP=api
```

### Running tests

```bash
make test                 # all
make test APP=web         # one app
make test PACKAGE=auth    # one shared package
```

## Architecture (cross-cutting)

- See `ARCHITECTURE.md` for monorepo-wide patterns.
- See `apps/<x>/ARCHITECTURE.md` for per-app architecture.
- Active monorepo-wide ADRs: `docs/adr/`.
- Per-app ADRs: `apps/<x>/docs/adr/`.

## Cross-cutting concerns

- **Shared schemas**: `packages/shared-types/` is the single source of truth; consumed by all apps.
- **Authentication**: `packages/auth/` provides the OIDC client used by all apps.
- **UI components**: `packages/ui-components/` for shared design system.
- **Linting / formatting**: per-language; orchestrated at root.
- **Dep management**: each language has its own lockfile; root `Makefile` orchestrates updates.
- **Versioning**: {{independent per app, OR fixed across monorepo, OR Changesets-style, pick and document}}

## Releases

- Apps: deployed independently per their CI/CD.
- Packages: versioned per their own SemVer; consumers pin.
- Root-level releases (if any): for monorepo-wide tooling versions.

## Documentation

- This README, top-level navigation
- `ARCHITECTURE.md`, cross-cutting
- `SECURITY.md`, disclosure policy
- `CHANGELOG.md`, root-level changes (tooling, structure)
- Per-app: `apps/<x>/README.md`, `apps/<x>/CHANGELOG.md`
- Cross-app runbooks: `docs/runbooks/`

## Contributing

See `CONTRIBUTING.md`. Per-app contributing nuances in `apps/<x>/CONTRIBUTING.md` if applicable.

## License

{{SPDX identifier}}
```

## Notes

- **Monorepo README is navigation-led.** Don't try to explain every app inline, link to per-app READMEs.
- **Build orchestrator choice is load-bearing**; document why (Turborepo for cache hit rates, Nx for affected-graph, Bazel for cross-language correctness, etc.).
- **Versioning model decision** (independent vs fixed vs changesets) is a top-3 monorepo decision; ADR it.
- **Avoid duplicating per-app docs** at the top level. Cross-link.
