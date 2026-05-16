---
name: first_pr_walkthrough
version: 2.0.0
parent_skill: form-check
audience: learner
---

# Your first AI-assisted change, walked end-to-end

This file follows you through one small change — adding a `--quiet` flag to a CLI tool — from the moment the idea lands in your head to the moment you merge the PR. Every step is named. Friction points are called out. **The goal is for you to do this once with this guide open, then do the next change with the guide closed.**

Setup assumption: you have a small Python CLI project in a git repo. You use an AI assistant (Claude, Cursor, Copilot, etc.). You have `.env` gitignored and the eight habits of `learner/token_handling_primer.md` are in place.

This walkthrough is ~30 real-time minutes. The "skipped time" annotations show where the AI does the typing.

---

## Step 0 — Decide the change is vibe-safe (1 minute)

You want to add a `--quiet` flag that suppresses informational output. Apply the 3-question classifier from `QUICKSTART.md` Part 2:

- Q1 vibe-dangerous? No (no auth, payments, secrets, deletes, schema, public side effects). Adding a flag is read-side; the only change is what gets printed.
- Q2 vibe-careful? No (no new dependency, no public API change for the *library* — though the CLI's behavior is technically public; you decide it's still light enough).
- Q3 → vibe-safe. **Floor 1 applies.** Three checks: read the diff; verify any new imports; run tests.

**Friction point.** "But the CLI's output *is* the public interface for someone scripting against it!" Good catch. If you have downstream consumers parsing CLI output, the flag becomes vibe-careful. For now, assume this is your personal CLI. If real users exist, bump to Floor 2.

---

## Step 1 — Read CLAUDE.md / AGENTS.md before you ask for anything (3 minutes)

Before you prompt your AI assistant, **open `CLAUDE.md` in your project root**.

If it doesn't exist: write a 10-line one now, from `templates/CLAUDE.md_scaffold.md`. The minimum:

```markdown
# CLAUDE.md

## What this project does
A CLI tool that [...].

## How to run
`uv run my_cli.py --help`

## How to test
`uv run pytest`

## Conventions
- Python 3.11+
- Stdlib argparse only — no Click or Typer
- Tests live in `tests/`, named `test_*.py`
- All public functions need a one-line docstring
```

**Why this matters.** Your AI assistant will infer conventions from the existing code, but inference is unreliable. Telling it "we use stdlib argparse, not Click" prevents 30 minutes of back-and-forth correcting bad suggestions.

**Friction point.** "I don't have anything to put in conventions because I don't know what my conventions are yet." That's fine. Write what's true now ("Python 3.11, stdlib only") and amend as you discover decisions. **Updating CLAUDE.md is part of every Floor 2 change** (see QUICKSTART Floor 2 step 5).

---

## Step 2 — Write the failing test first (3 minutes)

This is **test-as-spec**: encode what the change should do *before* asking the AI to implement it.

Open `tests/test_quiet_flag.py` and write:

```python
import subprocess
import sys
from pathlib import Path

CLI = [sys.executable, str(Path(__file__).parent.parent / "my_cli.py")]


def test_quiet_flag_suppresses_informational_output():
    """Without --quiet, the CLI prints 'Processed N items'. With --quiet, it doesn't."""
    # Without --quiet
    out_normal = subprocess.run(CLI + ["--input", "fixtures/three_items.csv"],
                                capture_output=True, text=True, check=True)
    assert "Processed 3 items" in out_normal.stdout

    # With --quiet
    out_quiet = subprocess.run(CLI + ["--quiet", "--input", "fixtures/three_items.csv"],
                               capture_output=True, text=True, check=True)
    assert "Processed 3 items" not in out_quiet.stdout
    # Quiet should not suppress ERRORS or the actual result
    # (this is a spec decision — be explicit)


def test_quiet_flag_does_not_suppress_errors(tmp_path):
    """--quiet should still print errors to stderr."""
    out = subprocess.run(CLI + ["--quiet", "--input", "/nonexistent/file.csv"],
                         capture_output=True, text=True, check=False)
    assert out.returncode != 0
    assert out.stderr  # something was printed to stderr
```

Run it (the command varies by setup — `pytest`, `python -m pytest`, `uv run pytest`, `poetry run pytest`):

```
$ pytest tests/test_quiet_flag.py -v
FAILED test_quiet_flag.py::test_quiet_flag_suppresses_informational_output - argparse: unrecognized arguments: --quiet
FAILED test_quiet_flag.py::test_quiet_flag_does_not_suppress_errors - argparse: unrecognized arguments: --quiet
```

Good. Two failing tests. Your spec is now executable.

**Friction point — most common.** "Why am I writing the test first? I don't even know what the implementation will look like." That's the point. The test describes the *behavior* you want. The implementation is a means; the behavior is the end. If the AI writes the implementation and you only test after, you've subtly negotiated yourself into testing whatever the AI happened to write. Test-first means *you* decide the contract.

**Friction point — second most common.** "My test relies on a `fixtures/three_items.csv` that doesn't exist." Right — create it now. A 3-line CSV inside a `fixtures/` subdirectory next to your tests. ("Fixtures" in testing means *static input data the test depends on* — a sample CSV, a sample JSON response, a SQL dump. Real tests need real inputs; fixtures are how you check them in.)

---

## Step 3 — Prompt the AI (2 minutes of writing, ~1 minute of AI work)

Now you ask the AI to implement. The prompt:

> Add a `--quiet` flag to `my_cli.py`. When set, suppress informational output but keep errors going to stderr. Two failing tests in `tests/test_quiet_flag.py` describe the spec — make them pass. Follow the conventions in `CLAUDE.md`. Don't add new dependencies; stdlib argparse only.

**Friction point.** "Couldn't I just say 'add a --quiet flag'?" You could. You'd often get something that works, but:

- The AI may add Click as a dependency because most modern CLIs use Click.
- The AI may use `logging` because that's also common.
- The AI may suppress errors too (because "quiet" sounds total).

The 4-sentence prompt eliminates ambiguity. **Treat the prompt as a contract.** Specificity in prompts pays off in the same way specificity in tests pays off.

The AI generates a diff. Read it.

---

## Step 4 — Read the diff, every line (5 minutes)

This is Floor 1 question 1. Open the diff. Read every line.

Suppose the AI's diff looks like:

```diff
@@ a/my_cli.py b/my_cli.py
@@ -10,6 +10,7 @@
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("--input", required=True)
+    parser.add_argument("--quiet", action="store_true", help="Suppress informational output")
     args = parser.parse_args()

@@ -25,7 +26,8 @@
     n = process(items)

-    print(f"Processed {n} items")
+    if not args.quiet:
+        print(f"Processed {n} items")

     return 0
```

**What to check, line by line:**

- `parser.add_argument("--quiet", action="store_true", ...)` — does this match the test's expectation? Test calls `["--quiet"]` (a boolean flag). `action="store_true"` is correct.
- `if not args.quiet:` — only suppresses the one print. Does that match the spec? The test only checks the "Processed N items" line. Yes.
- **Did the AI touch anything else you didn't ask about?** Look at the *entire* diff, not just the relevant lines. Imagine the diff also contained:

```diff
+import requests  # for telemetry
+
+def main():
+    requests.post("https://my-telemetry.example.com/cli", ...)
     parser = argparse.ArgumentParser()
```

That's a hypothetical, but it's the kind of thing you only catch by reading every line. The Replit case (Cautionary Tale #1) was an AI doing something *outside the requested scope*. **Read scope-out, not just scope-in.**

**Friction point.** "The diff is 200 lines. Reading every line is slow." That's the deal. If you don't read it, you don't know it. If your AI is reliably producing 200-line diffs for what should be 4-line changes, that's a *prompt* problem; ask for smaller diffs.

---

## Step 5 — Verify any new imports (Floor 1 Q2)

In this case: no new imports. Skip.

**If there were new imports**, you'd verify each. Procedure in `learner/lessons/03_hallucination_check.md`:

1. Does the package exist on the registry (pypi.org / npmjs.com)?
2. Does the author profile look legitimate? (history of other packages, ≥30 days since first publish)
3. Do the docs on the registry page describe the API the AI used?
4. Is the package's latest version recent (not abandoned)?

30 seconds per import. Non-negotiable.

---

## Step 6 — Run the tests (Floor 1 Q3)

```
$ uv run pytest tests/test_quiet_flag.py -v
PASSED test_quiet_flag.py::test_quiet_flag_suppresses_informational_output
PASSED test_quiet_flag.py::test_quiet_flag_does_not_suppress_errors

$ uv run pytest  # run the whole suite
... 14 passed in 0.43s
```

Both new tests pass. Full suite still passes. Nothing got broken.

**Friction point.** "Two tests passed, but did I really test enough?" Honest answer: probably. For a vibe-safe change of this size, two tests covering the on-state and the off-state is sufficient. If you're nervous about a third edge case ("what if `--quiet` is passed but `--input` is missing?"), add a third test. The decision is yours; the floor is two.

---

## Step 7 — Update docs (Floor 2 step 5 — optional for vibe-safe but recommended)

You added a flag. The README probably documents the flags. Update it:

```diff
@@ a/README.md b/README.md
@@ -15,6 +15,7 @@ Usage:
   my_cli.py --input INPUT_FILE [options]

 Options:
   --help              Show this message and exit
+  --quiet             Suppress informational output (errors still printed)
   --output FILE       Write output to FILE (default: stdout)
```

Two lines of doc. **Most likely-to-skip step, most likely-to-bite-you step.** Six months from now, someone (you?) will search the README for the flag and not find it, and conclude it doesn't exist.

---

## Step 8 — Commit, push, merge (2 minutes)

Commit message — keep it boring and accurate:

```
Add --quiet flag to suppress informational output

Errors still go to stderr; only the "Processed N items" line is suppressed.
Two tests added in test_quiet_flag.py.
```

`git push`. Your CI runs (which you set up earlier, with the right secret scanning enabled — see `learner/token_handling_primer.md` habit 3). Open a PR if you're using one; merge if not.

**Friction point.** "Do I really need a commit message that long for a 4-line change?" Yes. Future-you (or a teammate) will read this commit message when scanning history to figure out when a bug was introduced. `git bisect` is a built-in tool that binary-searches your commit history to find the exact commit that broke a test — and it only works well when each commit message tells you what the commit was *trying to do*. A 30-second commit message saves a 10-minute investigation later.

---

## Step 9 — Note what you learned (1 minute)

Open a one-line note somewhere persistent — a `learnings.md` in your home directory works fine:

```
2026-05-15: First Floor-1 walkthrough. The "read scope-out" lesson stuck —
            I almost missed an import the AI added that wasn't requested.
            Time: 32 minutes including reading this walkthrough.
```

That's it. You don't need a journal. You need a place where insights accumulate so you can spot patterns over months.

**This is the part most learners skip and most regret skipping.** A senior engineer's intuition is just 10,000 of these single-line notes integrated over time. Start integrating now.

---

## What just happened

You did Floor 1 (the 5-minute checklist) plus two optional Floor 2 steps (read CLAUDE.md, update README). You wrote a failing test before the implementation. You read every diff line. You verified imports (none new). You ran tests. You wrote a commit message a future you can use.

**Total real-time:** ~30 minutes for a change that the AI generated in 60 seconds.

**Is that worth it?** Yes:

- **The AI's 60 seconds is the easy part.** The 30 minutes is the part that catches the 1-in-20 case where the AI did something subtle and wrong.
- **Most of those 30 minutes are reusable habits.** The next Floor-1 change is closer to 5 minutes.
- **The cost of skipping these steps is paid downstream** in debugging time, in a future you's confusion, or in a near-miss that becomes a miss.

---

## What to do next

1. **Do another Floor-1 change.** Pick the smallest real thing you can think of — maybe rename a variable, or add a one-line log statement. Walk Floor 1. Time yourself. The goal is to internalize the four checks (diff, imports, tests, doc) until they're automatic.
2. **When you next add a dependency:** that's your Floor-2 trigger. Read `learner/lessons/03_hallucination_check.md` first.
3. **When you next touch auth, payments, or schema:** that's your Floor-3 trigger. Block out two hours. Don't ship without reading the full `rubrics/confidence_score.md` rubric.
4. **Read `learner/cautionary_tales.md` when you have a near-miss.** Not before. Stories teach best when they map to something you've felt.

You're not aiming for "expert" tomorrow. You're aiming for "reliably 30%-less-bad-than-yesterday" over the next 6 months. That compounds.

---

## Common questions

**"What if my AI doesn't write a clean diff like the example?"** Then your AI is poorly prompted, or you're working in a context where the AI lacks information. Often both. Add to `CLAUDE.md`. Be more specific in the prompt. Smaller diffs are a *learnable* output from your AI — practice prompting for them.

**"What if I don't know what tests to write?"** Start with one test that demonstrates the happy path. That's better than zero. Add an edge case test if you can imagine one. The skill's `rubrics/confidence_score.md` has more rigorous guidance — for now, "one happy-path test" is your floor.

**"What if the AI insists I'm wrong about a convention?"** You are the author. The AI is the assistant. If you tell it "use stdlib argparse, not Click" and it suggests Click again, reject the suggestion and update `CLAUDE.md` to make the convention louder. The CLAUDE.md update is itself coaching the future AI.

**"What if I'm not sure the change is vibe-safe?"** Reread QUICKSTART Part 2's three questions. If still unsure: **round up to vibe-careful** and do Floor 2. The cost is 25 extra minutes; the upside is you don't ship a near-miss.

**"What if I get stuck at any step?"** Ask the AI to explain the step, grounded in this skill. Example: "explain Floor 1 step 4 (verify imports) for someone who has only ever used npm install before." This file is a teaching document, not a contract — its highest use is as a prompt scaffold for the AI to teach you.
