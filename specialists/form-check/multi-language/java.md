---
name: java_kotlin_tooling
version: 2.0.0
parent_skill: form-check
gate: scale-up-friendly (default-OK; depth in scale-up/spring_kotlin_jvm.md)
---

# Java / Kotlin, tooling depth

This file covers default-mode JVM tooling (Maven / Gradle, JUnit 5, etc.). Spring Boot 3 + Kotlin coroutines deep-dive is in `scale-up/spring_kotlin_jvm.md` (gated; for enterprise greenfield with JVM forcing constraint).

## Tooling matrix

| Concern | Java tool | Kotlin tool |
|---|---|---|
| Test runner | JUnit 5 | JUnit 5 (via kotlin-test or kotest) |
| Property-based | jqwik | kotest property |
| Mutation | pitest | pitest (kotlin support) |
| Linter | Spotless + ErrorProne + Checkstyle | detekt + ktlint |
| Type checker | (compile-time) | (compile-time) |
| Formatter | Spotless (google-java-format) | ktlint |
| Dep audit | OWASP Dependency-Check; Snyk; gradle-versions-plugin | same |
| Lockfile | gradle-dependency-verification (`metadata.xml`) | same |
| Fuzzing | jazzer / OSS-Fuzz | jazzer |
| Secrets scan | trufflehog / gitleaks | same |
| SBOM | cyclonedx-maven-plugin / cyclonedx-gradle-plugin | same |
| Build | Maven OR Gradle 8+ | Gradle 8+ (Kotlin DSL preferred) |

## Test-as-spec example (Kotlin + kotest)

```kotlin
// src/test/kotlin/HtmlTruncationSpec.kt
import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.ints.shouldBeLessThanOrEqual
import io.kotest.matchers.shouldBe
import io.kotest.property.Arb
import io.kotest.property.arbitrary.string
import io.kotest.property.checkAll

class HtmlTruncationSpec : StringSpec({
    "truncation is idempotent" {
        checkAll(Arb.string(0..10_000)) { html ->
            val once = truncateHtml(html, 3000)
            val twice = truncateHtml(once, 3000)
            twice shouldBe once
            once.length shouldBeLessThanOrEqual 3000
        }
    }
})
```

## Fitness function example (lint-class with ArchUnit)

```java
// src/test/java/architecture/BoundaryTest.java
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

@AnalyzeClasses(packages = "com.example")
public class BoundaryTest {
    @ArchTest
    static final ArchRule core_does_not_depend_on_api =
        classes().that().resideInAPackage("..core..")
                 .should().onlyDependOnClassesThat()
                 .resideInAnyPackage("..core..", "..shared..", "java..");

    @ArchTest
    static final ArchRule api_can_depend_on_core =
        classes().that().resideInAPackage("..api..")
                 .should().onlyDependOnClassesThat()
                 .resideInAnyPackage("..api..", "..core..", "..shared..", "java..", "jakarta..", "org.springframework..");
}
```

ArchUnit is the canonical JVM fitness-function library; rules run as JUnit tests.

## Common pitfalls

- **Maven Central without checksum verification**: enable `gradle-dependency-verification` or Maven's `enforcer` plugin.
- **Jackson `@JsonAutoDetect` over public fields**: mass-assignment risk (CWE-915 / OWASP API3:2023). Use `@JsonProperty` allowlist.
- **`new SecureRandom()` without seed care**: actually fine on modern JVMs (uses OS CSPRNG); the anti-pattern is `new Random()` for security.
- **Java serialization (`Serializable`)**: deserialization gadget chains. Prefer JSON / Protobuf; if forced, allowlist with `ObjectInputFilter` (Java 9+).
- **`Thread.sleep` instead of structured concurrency**: with virtual threads (Java 21+), use `StructuredTaskScope`.
- **JNI / Unsafe without ownership tracking**: GC won't help.
- **Logging frameworks (Log4j, Logback) misconfig**: Log4Shell-class CVE. Pin and audit.
- **JDBC string concatenation**: SQL injection. Always parameterized.
- **Spring `@Autowired` field injection**: harder to test; use constructor injection.

## Concurrency

Java 21+: virtual threads (`Thread.ofVirtual()`) + `StructuredTaskScope` is the new default. Replaces a lot of explicit reactive patterns (RxJava, Project Reactor) in straightforward request-handling code.

Kotlin: coroutines (`suspend fun` + `kotlinx.coroutines`), structured by design (parent-child cancellation).

For both: avoid `CompletableFuture` for new code unless integrating with legacy.

## Build choice

Gradle 8+ with Kotlin DSL is the modern default. Maven remains common in legacy enterprise; if forced, use Maven 3.9+ with the `enforcer` plugin and explicit dependency-management section.

For polyglot monorepos: Bazel / Pants if cross-language build dep tracking is the actual problem; otherwise Gradle composite builds suffice.
