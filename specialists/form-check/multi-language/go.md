---
name: go_tooling
version: 2.0.0
parent_skill: form-check
---

# Go, tooling depth

## Tooling matrix

| Concern | Tool |
|---|---|
| Test runner | `go test` + `testify` (assertions) + `gomock` (mocks) |
| Property-based | gopter or rapid |
| Mutation | go-mutesting or ooga |
| Linter | golangci-lint (aggregator: govet, staticcheck, errcheck, ineffassign, gosec, ...) |
| Formatter | gofmt + goimports (or gofumpt for stricter) |
| Dep audit | govulncheck (official) + Snyk |
| Lockfile | `go.sum` (always commit; hash-pinned by default) |
| Fuzzing | native `go test -fuzz` (1.18+) |
| Secrets scan | trufflehog / gitleaks |
| IaC lint | tfsec / checkov |
| SBOM | cyclonedx-gomod / syft |

## Test-as-spec example

```go
// internal/auditor/truncate_test.go
package auditor

import (
    "strings"
    "testing"

    "pgregory.net/rapid"
)

func TestTruncationIdempotent(t *testing.T) {
    rapid.Check(t, func(t *rapid.T) {
        html := rapid.StringMatching("[\\p{L}\\p{N}<>/= ]*").Draw(t, "html")
        once := TruncateHTML(html, 3000)
        twice := TruncateHTML(once, 3000)
        if twice != once {
            t.Errorf("not idempotent: %q vs %q", once, twice)
        }
        if len(once) > 3000 {
            t.Errorf("exceeds budget: len=%d", len(once))
        }
    })
}

func FuzzTruncate(f *testing.F) {
    f.Add("<p>hello</p>")
    f.Fuzz(func(t *testing.T, html string) {
        out := TruncateHTML(html, 3000)
        if len(out) > 3000 {
            t.Errorf("budget exceeded: %d", len(out))
        }
        // never end mid-tag
        if strings.LastIndex(out, "<") > strings.LastIndex(out, ">") {
            t.Errorf("split tag: %q", out)
        }
    })
}
```

## Fitness function example (lint-class)

`tools/check_boundaries.go`:

```go
// Forbid imports from internal/ outside their package.
// ADR: docs/adr/0007-module-boundaries.md.
package main

import (
    "fmt"
    "go/parser"
    "go/token"
    "os"
    "path/filepath"
    "strings"
)

var allow = map[string]map[string]bool{
    "core": {"core": true, "shared": true},
    "api":  {"api": true, "core": true, "shared": true},
}

func main() {
    fset := token.NewFileSet()
    var violations []string
    filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
        if !strings.HasSuffix(path, ".go") || strings.HasSuffix(path, "_test.go") {
            return nil
        }
        parts := strings.Split(filepath.Dir(path), string(os.PathSeparator))
        if len(parts) < 2 {
            return nil
        }
        pkg := parts[1]
        if _, ok := allow[pkg]; !ok {
            return nil
        }
        f, err := parser.ParseFile(fset, path, nil, parser.ImportsOnly)
        if err != nil {
            return err
        }
        for _, imp := range f.Imports {
            top := strings.Trim(imp.Path.Value, "\"")
            top = strings.Split(top, "/")[0]
            if _, internal := allow[top]; internal && !allow[pkg][top] {
                violations = append(violations, fmt.Sprintf(
                    "%s imports %q (pkg %s allow=%v)", path, top, pkg, allow[pkg]))
            }
        }
        return nil
    })
    for _, v := range violations {
        fmt.Println(v)
    }
    if len(violations) > 0 {
        os.Exit(1)
    }
}
```

Or use `arch-go` / `go-arch-lint`, community options, less mature than ArchUnit.

## Common pitfalls

- **`http.Client{}` without `Timeout`**: hangs forever. Always set; default is 0 = no timeout.
- **Goroutine leaks**: spawn without cancellation context. Always `select` on `ctx.Done()`.
- **`defer` in a loop**: stack accumulates until function returns. Refactor.
- **`error` ignored**: `result, _ := ...`, `errcheck` lint catches.
- **String concatenation in SQL**: parameterize. `database/sql` requires `?` / `$1` placeholders.
- **`crypto/md5` for security**: never. Use SHA-256+ for non-passwords; argon2id / scrypt for passwords.
- **Public-by-default exported fields**: capitalization controls export; design carefully.
- **`os.Setenv` in tests**: pollutes environment across tests. Use `t.Setenv` (1.17+).
- **`json.Unmarshal` into `map[string]interface{}` without struct**: defeats type safety; use defined struct.

## Concurrency

Goroutines + channels are the model. **Use `context.Context` everywhere** for cancellation; never spawn a goroutine without a way to stop it.

For structured concurrency: `errgroup` + `context` is the closest stdlib analog to nurseries. `sync.WaitGroup` works for fire-and-forget but doesn't propagate errors.

Avoid `goto`. Avoid named return values for non-trivial functions (they obscure flow).

## Module hygiene

- `go.mod` declares dependencies; `go.sum` pins hashes (commit always).
- `go mod tidy` after every dep change; verify `go.sum` diff in PR.
- `GOFLAGS="-mod=readonly"` in CI to refuse implicit dep adds.
- `govulncheck ./...` in CI; fail on any actual vuln (vs unreachable).
