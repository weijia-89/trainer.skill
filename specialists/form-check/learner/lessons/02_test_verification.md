---
name: lesson_02_test_verification
version: 2.0.0
parent_skill: form-check
audience: learner
rubric_component: 2
---

# Lesson 2 — Test verification

**The pitch.** Tests are how you encode "what I meant" so you can prove an AI wrote what you meant. They are not just safety nets; they are *the contract*.

---

## The 90-second version

For every AI-assisted change:

1. **Tests exist for the new behavior.** If new behavior added: at least one happy-path test exists.
2. **Tests ran.** You actually executed them and observed `PASS`. Reading "it should pass" in the AI's output is not running.
3. **You captured before/after.** Before the change: what did the suite look like? After: what does it look like now? Did you accidentally make a previously-failing test pass for the wrong reason?

For Floor 2 and Floor 3, add: **mutation score on touched code meets the tier target** (see `rubrics/confidence_score.md`).

---

## Why this matters

Two reasons.

**Reason 1: test-as-spec is the only way to get unambiguous AI output.**

If you ask an AI "add a `--quiet` flag," you can get a working flag that:

- Suppresses *all* output (including errors)
- Suppresses only stdout, not stderr
- Suppresses only one specific log line
- Suppresses output but breaks an existing integration with another tool

All of those are arguably "a `--quiet` flag." If you didn't write a test first, *whichever one the AI happened to pick is now your spec*.

Tests-as-spec means: you write what `--quiet` should do (in test code), then the AI implements something that makes those tests pass. The contract is unambiguous.

**Reason 2: AI-generated code passes tests that hide bugs.**

Academic studies of AI-Copilot-generated code correctness and security (2023–2025; see `references/notes.md` for the cited papers) found that AI-generated code:

- Frequently passes the developer's tests
- Sometimes does so by re-implementing the test's assumption rather than the test's intent
- Often has latent bugs in code paths the developer didn't think to test

That last point is the killer. **The AI writes the code; the AI may also have written the tests; the tests cover what the AI thought to cover.** Mutation testing (described below) catches gaps the AI missed because it didn't think about them.

---

## The full process

### Step 1: write the failing test first (test-as-spec)

This is the test-as-spec principle. **Before you ask the AI to implement**, write a test that describes the behavior. The test should fail (because the implementation doesn't exist yet). When the AI's implementation is in, the test should pass.

What to test:

- **One happy-path case.** "The function does the right thing when called normally."
- **One edge case.** "The function handles the empty list / None / negative input / etc. correctly."
- **One error case** if the function can fail. "The function raises the right exception when given bad input."

Three tests per function is a floor for vibe-safe. Floor 2 / 3 need more (see rubric mutation-score targets).

### Step 2: run the tests, observe the output

```
$ pytest          # or: npm test, cargo test, go test ./..., etc.
... 14 passed, 0 failed in 0.43s
```

**The number you record is `14 passed, 0 failed`.** Not "the tests run cleanly" — the *count*. If a future change adds a test that runs but doesn't get counted because it's a new file that wasn't picked up, you want to notice the count change.

### Step 3: before-and-after comparison

Before merging:

- Run the suite *before* applying the change. Note the count.
- Apply the change.
- Run the suite *after*. Note the count.
- Did the change *add* tests? Did it *remove* tests?
- Did any test go from `PASS` to `FAIL` or vice versa for unexpected reasons?

A surprisingly common failure: the AI's implementation makes a previously-failing test pass *for the wrong reason* (e.g. it changed the test's assertion, not the implementation's behavior). Reading the diff catches this (Lesson 1); the count-and-status check is a second line of defense.

### Step 4 (Floor 2/3 only): mutation score

**Mutation testing** is a way to ask: "if I subtly broke the implementation, would the tests catch it?"

A mutation testing tool generates many small "mutants" of your code — change `==` to `!=`, swap `>` for `>=`, delete a line, etc. — and re-runs the tests for each mutant. Each mutant has two outcomes:

- **Killed:** the test suite caught the mutation (good).
- **Survived:** the test suite *didn't* catch the mutation (a test gap).

Mutation score = killed / total. Higher is better.

Tier targets (from `rubrics/confidence_score.md`):

| Language | Tool | Vibe-dangerous | Vibe-careful | Vibe-safe |
|---|---|---|---|---|
| Python | `mutmut` / `cosmic-ray` | ≥75% | ≥60% | ≥40% |
| TypeScript / JS | Stryker | ≥75% | ≥60% | ≥40% |
| Go | `go-mutesting` | ≥70% | ≥55% | ≥35% |

**You compute mutation score on touched code, not the whole codebase.** That's the column "operates on the diff" — fast (seconds-to-minutes), focused.

If your host environment can't run mutation testing: the rubric specifies you score test-verification at most 60 out of 100 and document the gap. Don't fake it.

---

## What goes wrong

### Failure mode A: the AI wrote the test *and* the implementation

You asked the AI to "add tests for the new function." It did. The function passes its own tests. **This proves nothing.** The AI wrote both sides; it's not a contract, it's an echo.

**Rule:** *you* write at least the test signatures and the assertions. The AI fills in only the implementation. Test-as-spec means *you* hold the spec.

### Failure mode B: the test runs but the test is trivial

```python
def test_quiet_flag():
    assert True  # TODO: add real assertion
```

Tests like this exist in production codebases. They pass. They prove nothing. **A test that doesn't assert against the actual behavior is not a test; it's a comment.**

**Rule:** every test has at least one assertion against the *output* of the code under test, not against a tautology.

### Failure mode C: counting "tests pass" without running them

You read the AI's diff. It includes test code. The AI's commentary says "the tests should pass." **You did not run them.** This happens more than you'd think — the AI's confident summary feels like evidence.

**Rule:** run the tests. Observe the count. Then trust.

### Failure mode D: test fixtures that mock too much

You wrote a test for "the function calls the external API and returns the result." Your test mocks the external API. The mock returns whatever you set it to return. **The test now proves "the function does *something* when the API returns what we told it to return."** That's not what the test was for.

This is a long-tail problem and worth a dedicated study (search "mock heavy testing pitfalls"). For now: be aware that mocking can erase the value of a test if you mock the thing the test was supposed to verify.

### Failure mode E: the test depends on time / environment

```python
def test_birthday_email():
    assert send_birthday_email(user) == "Happy birthday, Alice!"
```

This test passes today, fails tomorrow (different date). Tests that depend on `now()`, environment variables, network reachability, or file paths from your machine are **flaky** — they pass sometimes and fail sometimes.

**Rule:** every test sets up the conditions it needs. Use `freezegun` (Python) / `MockDate` (JS) for time, in-memory fixtures for the file system, mocks for external calls — *and* mark when the test is integration vs. unit so you can choose to run them separately.

---

## When test verification gets relaxed

For pure documentation changes (`docs/`, `README.md`, comments), there's nothing to test. Mark these explicitly:

> This is a doc-only change. Test verification: n/a.

For everything else: there is no "too small to test." A one-line change can break things. A function rename can update 19 callers and miss one. **Tests are the floor.**

---

## Exercises

### Exercise 1: test-first a small change

Pick something tiny to add to a project you're working on. Maybe a utility that capitalizes a name. Before asking the AI to implement:

```python
# tests/test_capitalize.py
def test_capitalize_simple():
    assert capitalize("alice") == "Alice"

def test_capitalize_already_capital():
    assert capitalize("ALICE") == "Alice"

def test_capitalize_empty():
    assert capitalize("") == ""
```

Run the tests. They fail (module doesn't exist). Now ask the AI to implement `capitalize` such that these tests pass. **Notice how unambiguous your request is.**

### Exercise 2: ask the AI to break your tests

After a real change has shipped (don't do this in production code), ask the AI: "introduce one subtle bug in `function_name` that my tests don't catch." If the AI succeeds, that's a test gap. Write the missing test. Now your tests are stronger.

This is mutation testing by hand. It's slower than `mutmut` but doesn't require setup, and it teaches you what mutation testing actually does.

### Exercise 3: count and check

For your current project: run the test suite. Note the count. Now run it again with verbose output (`pytest -v`). Read every test name. **Can you tell what each test asserts from the name?** If three tests are named `test_thing_1`, `test_thing_2`, `test_thing_3`: those names lie to you. Rename them to describe the assertion.

---

## Cross-references

- **Rubric component 2** in `rubrics/confidence_score.md` — weight 20 (the highest single-component weight). Mutation-score table is here.
- **First-PR walkthrough Step 2** (test-as-spec demonstrated) in `learner/first_pr_walkthrough.md`.
- **Lesson 1 (code-read depth)** — tests don't replace reading.
- **Mini-runbook in `SKILL.md` Section 10** — test-as-spec is step 3.

---

## Retrieval prompts

Per `learner/study_protocol.md` Habit 1 (retrieval beats re-reading): **close this file** and answer the questions below in writing or aloud. Then re-open and check.

If you miss two or more, schedule a re-read for **+3 days** (Habit 2 — spacing).

1. Close this file. State the test-as-spec principle in one sentence.
2. What's the difference between *running* tests and *verifying* tests? Name two checks the second includes that the first doesn't.
3. What is mutation testing, and what does a mutation score of 50% tell you that a coverage score of 95% can't?
4. Recall three common failure modes where AI-written code passes its tests but is still wrong.

When you've answered all four cold (no peeking) on two separate occasions ≥1 week apart, this lesson has stuck. Move it to your spaced-review monthly cadence.
