---
name: rust_tooling
version: 2.0.0
parent_skill: form-check
---

# Rust, tooling depth

## Anti-fixation clause

This file is tooling guidance, not a mandate. Trainer does not enforce any single language. Language selection is domain-conditional (web/client → TypeScript; ML/data/eval → type-checked Python; simple servers → Go; correctness/perf/FFI → Rust). A mechanical correctness gate, not the language name, is the lever that reduces silent-bug surface in LLM-generated code. See `references/llm_code_correctness_gate.md`.

## Tooling matrix

| Concern | Tool |
|---|---|
| Test runner | `cargo test` + `cargo nextest` (preferred for parallelism) |
| Property-based | proptest or quickcheck |
| Mutation | cargo-mutants |
| Linter | clippy (`cargo clippy --all-targets -- -D warnings`) |
| Formatter | rustfmt |
| Dep audit | cargo-audit (RustSec advisory DB) |
| Lockfile | `Cargo.lock` (always commit for binaries; commit for libs since 1.56) |
| Fuzzing | cargo-fuzz (libFuzzer) + loom (concurrency model checking) |
| Secrets scan | trufflehog / gitleaks |
| SBOM | cyclonedx-rust-cargo / syft |
| Allowed deps | cargo-deny |

## Test-as-spec example

```rust
// src/auditor.rs
use proptest::prelude::*;

fn truncate_html(html: &str, budget: usize) -> &str {
    if html.len() <= budget { html } else { &html[..budget] }
}

#[cfg(test)]
mod tests {
    use super::*;

    proptest! {
        #[test]
        fn truncation_is_idempotent(html in "\\PC{0,10000}") {
            let once = truncate_html(&html, 3000);
            let twice = truncate_html(once, 3000);
            prop_assert_eq!(once, twice);
            prop_assert!(once.len() <= 3000);
        }
    }
}

// src/auditor.rs (fuzz target via cargo-fuzz)
// in fuzz/fuzz_targets/truncate.rs:
//
// #![no_main]
// use libfuzzer_sys::fuzz_target;
// use crate_under_test::truncate_html;
//
// fuzz_target!(|html: &str| {
//     let out = truncate_html(html, 3000);
//     assert!(out.len() <= 3000);
// });
```

## Fitness function example (lint-class)

`deny.toml` (for cargo-deny):

```toml
[bans]
multiple-versions = "warn"
deny = [
    { name = "openssl" },           # require rustls
    { name = "ring", version = "<0.17" },
]

[advisories]
vulnerability = "deny"
unmaintained = "warn"
yanked = "deny"

[licenses]
allow = ["MIT", "Apache-2.0", "Apache-2.0 WITH LLVM-exception", "BSD-3-Clause", "ISC"]
deny = ["GPL-2.0", "GPL-3.0", "AGPL-3.0"]
```

For module boundaries: a `cargo-deny` rule + per-crate visibility (`pub(crate)`, `pub(super)`) handles much of it natively. ArchUnit-equivalents like `archon` exist but are less mature.

## Common pitfalls

- **`unwrap()` / `expect()` in production code**: panics. Use `?` propagation + custom error types (thiserror).
- **`unsafe` without an `// SAFETY:` comment**: clippy `undocumented_unsafe_blocks` lint catches.
- **`thread::spawn` without `join`**: detached thread; resource leak. Use scoped threads (`std::thread::scope` 1.63+) or rayon / tokio.
- **`Mutex` poisoning ignored**: `lock().unwrap()` panics on poisoned mutex; choose `lock().unwrap_or_else(|p| p.into_inner())` only with reason.
- **`async fn` with `Send` boundary issues**: `Rc` and `RefCell` are not `Send`; use `Arc` / `RwLock` if crossing await points.
- **Blocking in async context**: `std::fs` / `std::thread::sleep` in tokio runtime → starves the runtime. Use `tokio::fs` / `tokio::time::sleep`.
- **`String` vs `&str` confusion at API boundaries**: prefer `&str` parameters and `String` returns; document ownership.
- **Trait-object overhead in hot paths**: `Box<dyn T>` involves vtable indirection; use generics where monomorphization wins.
- **`Drop` order in async**: `Drop` runs synchronously; for async cleanup, use `AsyncDrop` patterns or explicit `close()` methods.

## Concurrency

`async`/`await` + tokio is the dominant runtime; smol exists for simpler workloads. **Use `tokio::select!` for cancellation**; `JoinSet` for many tasks; `tokio_util::sync::CancellationToken` for explicit cancellation.

Channels: `tokio::sync::mpsc` (multi-producer, single-consumer) for most cases; `flume` for cross-runtime; `crossbeam-channel` for pure sync threads.

Concurrency model checking: `loom` simulates all interleavings of a synchronous concurrent test. Use for primitives and lock-free data structures; not viable for whole-program testing.

## Edition + MSRV

Set explicit MSRV in `Cargo.toml`:

```toml
[package]
edition = "2024"
rust-version = "1.85"
```

CI matrix tests against MSRV + stable + nightly to catch regressions.

## Where Rust earns its keep

- Embedded / no-std targets
- Memory or perf budget is the spec (justify in ADR)
- Long-running services where GC pauses unacceptable
- Cryptography / parsing untrusted input (memory safety + zero-copy)

Where Rust does not pay rent (default mode):
- Quick CLI tools, Go has 10× faster onboarding
- Forms-heavy CRUD, Rails / Django earn faster
- Data / ML adjacent, Python ecosystem dominates

Match the spec to the tool, not the tool to the project.
