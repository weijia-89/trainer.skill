---
name: spring_kotlin_jvm
version: 2.0.0
parent_skill: form-check
gate: forcing-constraint-required (org-mandate or enterprise greenfield with JVM team)
---

# Kotlin + Spring Boot 3 — JVM tooling depth

> **[GATED — informational only]** Forcing-constraint ADR required (typically: enterprise team uses JVM; greenfield where company-wide JVM mandate; M&A integration).
>
> Default-mode `form-check` covers Java/Kotlin tooling lightly in `multi-language/java.md`. This chapter is the depth.

## When this chapter applies

- Org has existing JVM platform team and tooling
- Greenfield service with JVM forcing constraint (talent pool, infra team, observability standardized on JVM)
- Migration of legacy Java to Kotlin

## Stack picks

| Layer | Choice | Reject |
|---|---|---|
| Language | Kotlin {{1.9+}} (or Java 21+) | Scala (smaller ecosystem; harder hiring); Groovy |
| Framework | Spring Boot 3.{{2}}+ with Spring Framework 6 | Quarkus / Micronaut (worth it for native-image; not the default) |
| Build | Gradle {{8+}} with Kotlin DSL | Maven (acceptable but Gradle wins ergonomically) |
| ORM | Spring Data JPA (with Hibernate) + Flyway migrations | jOOQ (great but less integrated) |
| HTTP | Spring MVC (servlet) OR Spring WebFlux (reactive) | Pick MVC unless you genuinely need reactive |
| Auth | Spring Security with OIDC | rolling your own |
| Concurrency | Virtual threads (Java 21+) OR Kotlin coroutines | reactive types in user-facing code |
| Testing | JUnit 5 + kotest (Kotlin) or JUnit 5 + AssertJ (Java) + MockK (Kotlin) / Mockito (Java) + Testcontainers | Spock (Groovy ecosystem drift) |
| Property-based | jqwik (Java) or kotest property (Kotlin) | quickcheck-style externals |
| Mutation | pitest | (no real alternative for JVM) |
| Lint / format | Spotless + ktlint (Kotlin) or google-java-format (Java); detekt (Kotlin); ErrorProne (Java) | Checkstyle (legacy) |
| Observability | Micrometer + OpenTelemetry | proprietary monitoring shim only |
| Architectural fitness | ArchUnit | (no real alternative) |
| Dep audit | OWASP Dependency-Check + gradle-dependency-verification + Snyk | none of these alone is enough; combine |
| SBOM | cyclonedx-gradle-plugin / cyclonedx-maven-plugin | manual |

## Spring Boot 3 specifics

- **Native image** (GraalVM): great for startup time + memory; tooling matured but reflection / dynamic-proxy patterns require explicit hints.
- **Virtual threads**: replace `@Async` patterns and Project Reactor in user-facing code where reactive isn't earning its keep.
- **Observability** (Spring Boot 3 default): Micrometer Tracing + OpenTelemetry exporter; auto-config is good; verify trace propagation across HTTP and message-driven boundaries.
- **Configuration**: prefer `@ConfigurationProperties` over `@Value`; type-safe; testable.
- **Secrets**: Spring Cloud Config / Vault integration / cloud-secrets-manager; never `application.yml` in repo.

## Kotlin idioms

- `data class` for DTOs; `value class` for type-safe primitives.
- `sealed class` / `sealed interface` for exhaustive matching (Kotlin 1.7+).
- Coroutines for I/O-bound work; structured by default (parent-child cancellation).
- Avoid `lateinit` outside of testing; prefer constructor injection.
- Prefer null-safety over `!!` operator; if you find yourself using `!!`, redesign.

## Architectural fitness — ArchUnit

ArchUnit rules are JUnit tests; they fail CI like any other test.

```kotlin
@AnalyzeClasses(packages = ["com.example"])
class ArchitectureTest {
    @ArchTest
    val core_does_not_depend_on_api = classes()
        .that().resideInAPackage("..core..")
        .should().onlyDependOnClassesThat()
        .resideInAnyPackage("..core..", "..shared..", "java..", "kotlin..")
}
```

## Common pitfalls

- **Spring Security misconfiguration** — default-deny is the right starting point; expose endpoints explicitly.
- **JPA n+1** — eager / lazy fetch surprises; use `@EntityGraph` or projections.
- **Transaction propagation** — `@Transactional` on private methods doesn't work; declarative-only on public.
- **Jackson polymorphic deserialization** — gadget-chain risk; allowlist via `@JsonTypeInfo` annotations carefully.
- **`@Async` on the same class** — proxy doesn't intercept self-invocation.
- **Field injection** — harder to test; prefer constructor.
- **Forgetting `@Validated`** — Bean Validation annotations only fire when the class is `@Validated`.
- **Maven Central without checksum verification** — enable `gradle-dependency-verification`.

## Concurrency on JVM

- **Virtual threads** (Java 21+) for blocking I/O — replaces a lot of explicit reactive patterns.
- **Kotlin coroutines** for cooperative suspension — structured by default.
- **Project Reactor / RxJava** — only when streaming semantics are essential and the team owns the reactive operator vocabulary.
- **`CompletableFuture`** — legacy; coroutines or virtual threads are more ergonomic.

## Build optimizations

- Gradle build cache (local + remote)
- Configuration cache (Gradle 8.5+)
- Parallel test execution
- Test categorization (`@Tag`) so unit tests run fast in pre-commit; integration in CI

## Anti-patterns

- Kotlin "stringly-typed" code — value classes exist for a reason.
- Spring annotations everywhere ("annotation soup") — keep architectural seams visible without annotations.
- Reflection-heavy patterns that break native image without compensating hints.
- "Reactive everywhere" without measurable benefit (Project Reactor adds complexity vs synchronous Spring MVC).

## Sunset

If JVM mandate is lifted (org consolidation, M&A unwind), assess whether the service should be ported. Spring services don't trivially port; budget the migration if pursued.

## Cross-references

- `multi-language/java.md` (default-mode JVM)
- `distributed_systems.md` (if decomposing the JVM monolith)
- `service_mesh.md` (if mesh forcing constraint)
