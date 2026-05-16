---
name: README_library_archetype
version: 2.0.0
parent_skill: form-check
voice: precise, code-led; minimal autobiography
---

# README archetype: Library

```markdown
# {{library-name}}

> One-sentence description. State the *primitive* the library provides, not the philosophy.

[![CI](badge)](url) [![Coverage](badge)](url) [![Package](badge)](url) [![Docs](badge)](url)

## Install

```bash
# Python
pip install {{lib}}
# or
uv add {{lib}}

# TypeScript / JS
pnpm add {{lib}}

# Java / Kotlin (Gradle Kotlin DSL)
implementation("com.example:{{lib}}:{{version}}")

# Go
go get github.com/example/{{lib}}@latest

# Rust
cargo add {{lib}}
```

## Quick example

(Code first. The shortest possible example showing the primary primitive in action.)

```{{language}}
{{realistic, runnable example — 5–15 lines}}
```

## Concepts

- **{{Primitive 1}}**: one-sentence definition. Cross-link `docs/` for depth.
- **{{Primitive 2}}**: ...

## Documentation

- **API reference**: {{generated docs URL — Sphinx / typedoc / Javadoc / godoc / rustdoc}}
- **Cookbook**: `docs/cookbook/` (recipes for common tasks)
- **Architecture**: `ARCHITECTURE.md`
- **Security**: `SECURITY.md`
- **Changelog**: `CHANGELOG.md`

## Compatibility

| Aspect | Versions |
|---|---|
| Language | {{Python ≥3.11 / Node ≥18 / Java ≥21 / Go ≥1.22 / Rust ≥1.85}} |
| Major dependencies | {{e.g. Pydantic v2.x; Spring Boot 3.x}} |
| Tested platforms | {{linux-amd64, linux-arm64, darwin, windows}} |

## SemVer

This library follows [Semantic Versioning](https://semver.org/). See `CHANGELOG.md` for the explicit MAJOR/MINOR/PATCH rules and the deprecation policy (`docs/deprecation_policy.md`).

## Performance

(If performance is a documented characteristic — micro-benchmark table, methodology link. If not, omit this section rather than fudge.)

## Contributing

See `CONTRIBUTING.md`.

## License

{{SPDX identifier}}
```

## Notes

- **Library README is API-led, not story-led.** Code first; docs after.
- **Compatibility table is non-negotiable** for libraries. Consumers will use it before reading anything else.
- **No "5-step quickstart"** for libraries with 30+ primitives. Quickstart shows the *most common primitive*; the rest belong in cookbook / API ref.
- **API reference generation tool** must be uniform-docstring-friendly. Per-archetype voice rules: API ref docstrings are *uniform*, README prose is *conversational*. See `templates/doc_voice.md`.
- **Performance claims need methodology** or omit entirely.
- **No "this is a high-quality library" copy** — let the API speak for itself.
