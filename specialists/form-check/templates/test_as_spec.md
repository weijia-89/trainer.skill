---
name: test_as_spec
version: 2.0.0
parent_skill: form-check
---

# Test-as-Spec (multi-language)

Write the **failing** test first. The signature and assertions are the spec the AI implements against. This collapses the ambiguity gap that drives slopsquatting and dead-branch bugs.

## Test layers

| Layer | When | Tools |
|---|---|---|
| Unit | pure functions, transforms, parsers | pytest / Vitest / JUnit5 / go test / cargo test |
| Property-based | parsers, serializers, idempotent transforms | Hypothesis / fast-check / jqwik / rapid / proptest |
| Integration | DB, file I/O, subprocess | language-native + tmp dir/db |
| Eval (golden) | LLM-shaped behavior | language-native + golden_dataset.json |
| Smoke | "the happy path runs end-to-end" | tag-marked tests, run last |
| Fuzzing | parser memory/edge bugs | Atheris / jazzer / native go-fuzz / cargo-fuzz |
| Mutation | rubric component 2 floor | mutmut / Stryker / pitest / go-mutesting / cargo-mutants |

Per-language detail: `multi-language/{python,typescript,java,go,rust}.md`.

## Pattern A, unit (illustrative; pick your language)

**Python (pytest)**:
```python
def test_extract_wcag_criterion_from_axe_v_4_x():
    raw = {"tags": ["wcag2aa", "wcag1410"]}
    assert axe_runner._extract_wcag_criterion(raw) == "1.4.10"

def test_extract_wcag_criterion_returns_none_when_absent():
    assert axe_runner._extract_wcag_criterion({"tags": []}) is None
```

**TypeScript (Vitest)**:
```ts
import { describe, it, expect } from "vitest";
import { extractWcagCriterion } from "../src/axe-runner";

describe("extractWcagCriterion", () => {
  it("extracts 1.4.10 from wcag1410 tag", () => {
    expect(extractWcagCriterion({ tags: ["wcag2aa", "wcag1410"] })).toBe("1.4.10");
  });
  it("returns null when absent", () => {
    expect(extractWcagCriterion({ tags: [] })).toBeNull();
  });
});
```

## Pattern B, property-based (round-trip / idempotency)

The most leverage-per-test pattern in this skill. Use for parsers, serializers, transforms.

(Examples in `multi-language/python.md`, `multi-language/typescript.md`, etc.)

## Pattern C, integration (tmp DB / file)

**Python**:
```python
def test_audit_persists_to_db(tmp_path):
    db = tmp_path / "audits.db"
    auditor.run("file:///tests/fixtures/html/missing_alt_001.html", db_path=db)
    rows = list(sqlite_utils.Database(db)["audits"].rows)
    assert len(rows) == 1
```

**Go**:
```go
func TestAuditPersists(t *testing.T) {
    dir := t.TempDir()
    db := filepath.Join(dir, "audits.db")
    if err := auditor.Run("file:///tests/fixtures/html/missing_alt_001.html", db); err != nil {
        t.Fatal(err)
    }
    rows := loadRows(t, db)
    if len(rows) != 1 { t.Errorf("got %d rows", len(rows)) }
}
```

## Pattern D, eval / golden dataset

```python
@pytest.mark.eval
def test_eval_baseline(golden_dataset, mock_llm):
    results = []
    for case in golden_dataset:
        result = auditor.run(case["url"], llm=mock_llm)
        results.append(score_against(result, case["expected"]))
    metrics = aggregate(results)
    baseline = json.load(open("eval_baseline.json"))
    for k, v in metrics.items():
        assert v >= baseline[k] - 0.02, f"{k} regressed: {v} < {baseline[k]}"
```

Sizing: 50–100 minimum, 200–500 prod-ready, 1000+ mature.

## Pattern E, review-gate test

Tests that fail if a vibe-dangerous gate is removed:

```python
def test_apply_destructive_requires_explicit_confirm():
    with pytest.raises(SystemExit):
        cli.main(["apply", "--config", "harden.yaml"])  # no --i-really-mean-it
```

```ts
it("apply requires explicit confirm flag", () => {
  expect(() => cli.main(["apply", "--config", "harden.yaml"]))
    .toThrow(/--i-really-mean-it/);
});
```

These are **fitness functions in disguise**, they encode the architecture decision (apply requires confirm) as an executable check.

## Pattern F, fuzzing (parsing untrusted input)

(See per-language files for syntax. Native fuzz support in Python (Atheris), Go 1.18+, Rust (cargo-fuzz), Java/JS (jazzer).)

Use for: parsers, deserializers, regex engines, anything taking untrusted bytes. Run as a CI job (long-running) or scheduled (nightly).

## Pattern G, mutation testing

Mutation tools introduce small program changes (mutants) and re-run tests. A mutation that survives = your test suite missed it.

Run on touched code in CI:

```bash
# Python
mutmut run --paths-to-mutate=src/auditor.py
mutmut results

# TypeScript
npx stryker run --mutate "src/**/*.ts"

# Java
mvn org.pitest:pitest-maven:mutationCoverage

# Go
go-mutesting ./internal/auditor/...

# Rust
cargo mutants -p crate-name
```

Tier floors per `rubrics/confidence_score.md`. **If host can't run mutation, score test-verification ≤ 60.**

## What "good" looks like

- Tests **read like the spec**. A non-implementer can reconstruct the contract from test names.
- Each test asserts **one thing** (or one logical claim with multiple supporting asserts).
- Property-based covers all parsers / serializers / transforms.
- Eval tests gate CI; baselines updated only after explicit human review.
- Mutation score ≥ tier floor on touched code.
- Fuzz job runs nightly on parsing surfaces.

## Common mistakes (vibe-coding tells)

- **Mocking what you should integration-test.** If you mock the DB in a test "for the DB layer", you've tested nothing.
- **Asserting the exact prompt string.** Tests should assert behavior, not prompt text.
- **No property-based for parsers.** Hypothesis / fast-check / proptest catches CWE-707 edges.
- **Eval baseline updated by script.** Always manual.
- **Tests pass but feature broken.** Coverage was path-exercising not behavior-asserting.
- **Time-dependent tests.** `Date.now()` / `time.now()` as input → flaky in CI. Inject clock.
- **Random non-deterministic tests.** No seed, no recording.
- **Subprocess without timeout in tests.** Hangs CI.
