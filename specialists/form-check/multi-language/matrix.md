---
name: multi_language_matrix
version: 2.0.0
parent_skill: form-check
---

# Multi-Language Tooling Matrix

Per-concern × language tooling. Pick the row that matches your stack; consult the per-language file for depth (`python.md`, `typescript.md`, `java.md`, `go.md`, `rust.md`).

## Tooling matrix

| Concern | Python | TypeScript / JS | Java / Kotlin | Go | Rust |
|---|---|---|---|---|---|
| **Test runner** | pytest | Vitest / Jest | JUnit 5 | `go test` | `cargo test` + `cargo nextest` |
| **Property-based** | Hypothesis | fast-check | jqwik | gopter | proptest / quickcheck |
| **Mutation testing** | mutmut / cosmic-ray | Stryker | pitest | go-mutesting | cargo-mutants |
| **Linter** | ruff | Biome / ESLint | Spotless + ErrorProne / detekt | golangci-lint | clippy |
| **Type checker** | mypy / pyright | tsc | (compile-time) | (compile-time) | (compile-time) |
| **Formatter** | ruff format / black | Biome / Prettier | Spotless | gofmt + goimports | rustfmt |
| **Dep audit** | pip-audit / safety | npm audit + Socket | OWASP DC + Snyk | govulncheck | cargo-audit |
| **Lockfile w/ hashes** | `uv lock --generate-hashes` | `pnpm-lock.yaml` integrity | gradle-dependency-verification | `go.sum` | `Cargo.lock` |
| **Fuzzing** | Atheris | jazzer / fast-check arbitrary | jazzer / Jazzer | go-fuzz / native fuzz | cargo-fuzz / loom |
| **Secrets scan** | trufflehog / detect-secrets | trufflehog / gitleaks | trufflehog / gitleaks | trufflehog / gitleaks | trufflehog / gitleaks |
| **IaC lint** | tfsec / checkov / kics | tfsec / checkov | tfsec / checkov | tfsec / checkov | tfsec / checkov |
| **SBOM tool** | cyclonedx-py / syft | cyclonedx-npm / syft | cyclonedx-maven-plugin / syft | cyclonedx-gomod / syft | cyclonedx-rust-cargo / syft |
| **Docs gen** | Sphinx + MyST | typedoc / TSDoc | Javadoc / Dokka | godoc | rustdoc |
| **Concurrency model** | Trio / AnyIO / asyncio | async/await native | virtual threads (Java 21+) / coroutines (Kotlin) | goroutines + channels | async/await + tokio |

## Choice rules per concern

### Test runner
- Python: pytest is canonical.
- TS: Vitest if Vite ecosystem; Jest for legacy. Avoid Mocha + Chai (more setup, no real benefit).
- Java/Kotlin: JUnit 5 always. Spock for behavior-style (Groovy).
- Go: `go test` + `testify` for assertion sugar.
- Rust: `cargo test` for unit; `cargo nextest` for parallelism + better output on large suites.

### Mutation testing tier targets

(See `rubrics/confidence_score.md` for full per-tier table.)

| Lang | Vibe-dangerous | Vibe-careful | Vibe-safe |
|---|---|---|---|
| Python | ≥75% | ≥60% | ≥40% |
| TS | ≥75% | ≥60% | ≥40% |
| Java/Kotlin | ≥80% | ≥65% | ≥45% |
| Go | ≥70% | ≥55% | ≥35% |
| Rust | ≥75% | ≥60% | ≥40% |

If host harness can't run mutation, score test-verification ≤ 60 and document.

### Property-based testing strategy

Use property-based for: parsers, serializers, transforms, idempotent ops, round-trip operations, comparators.

Don't use property-based for: integration with external services (use stubs + integration tests), randomized tests of UI rendering (flaky).

### Lockfile hash verification

All five ecosystems support cryptographic lock-file integrity. **Default-mode requires hash-pinned locks.** No `pip install -r requirements.txt` without `--require-hashes`. No `npm install` without `--strict-integrity`. No `gradle build` without `--verify-metadata`.

## When to walk this matrix

- Onboarding a new project: pick the row, populate `CLAUDE.md` Stack section.
- New-app planning: derive the test-as-spec scaffold from the stack row.
- Code review: check the project actually uses the row's tooling; flag gaps.
- Multi-language project: each language has its own row; document polyglot CI in CLAUDE.md.

## Polyglot project guidance

A monorepo or service spanning ≥2 languages should:

1. Document each language's row in `CLAUDE.md` Stack section.
2. CI runs each language's tooling in parallel.
3. Common concerns (secrets scan, IaC lint, SBOM) run once at repo root.
4. Avoid cross-language tooling that duplicates per-language tools (e.g. don't use `semgrep` for Python lint when ruff already covers it).

## Anti-patterns

- "We don't need mutation testing" — without measured floor on test verification, don't claim test-verification full credit.
- "Lockfile but no hashes" — defeats the lock's security purpose.
- "Vendored deps without provenance" — the lockfile is the provenance; vendoring without a lockfile re-introduces the slopsquatting attack surface.
- "One linter for all languages" — language-aware tools beat language-agnostic ones for false-positive rate.
