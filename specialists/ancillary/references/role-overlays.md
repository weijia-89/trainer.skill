# Role overlays

The base agent prompt at `../templates/agent-prompt.md` is `code`-flavored by default. Two overlays cover the other typical workloads. To apply an overlay, replace the relevant sections of the base template with the substitutions below; everything else (worktree setup, baseline capture, commit-no-push, session log) stays the same.

---

## Overlay: `Role: code` (default; included in base template)

The base template is already calibrated for this archetype. No substitutions.

**Typical use cases:**

- Implement a feature against a TDD plan
- Fix a failing test
- Refactor a function with regression-test coverage

**Verification shape (already in base):**

- Test count same or higher than baseline
- Failing-test names unchanged
- Ruff/lint clean
- Type checks pass (when applicable)

---

## Overlay: `Role: sweep`

Narrow-scope mechanical edits across many files. The work is largely find-and-replace with judgment, not architecture.

**Typical use cases:**

- Em-dash sweep across docs + tests
- Import rename after a module move
- Voice-rule audit applying a banned-pattern list
- File-permission or licence-header normalization

**Substitutions:**

Replace the `Task` section with:

```markdown
## Task

Apply <SWEEP_RULE> across <SCOPE_PATHS>. The rule and its replacement pattern are defined as:

- Pattern to detect: `<REGEX_OR_STRING>`
- Replacement: `<REPLACEMENT_OR_RULE>`
- Edge cases that do NOT match: <LIST>

Files in scope:

- <PATH_1>
- <PATH_2>
- <PATH_N>

Files explicitly out of scope (do NOT sweep): <LIST>
```

Replace the `Vibe-careful protocol` section with:

```markdown
## Sweep discipline

Sweep edits are vibe-safe per file but vibe-careful in aggregate. The risks are:

- False positives: pattern matches in contexts where it should be preserved (code blocks, embedded examples, citation strings). Read every match before edit.
- False negatives: pattern variants the regex did not anticipate. Run the verification grep after every batch of ~10 files; investigate any residual matches.
- Scope creep: the temptation to fix adjacent issues. STOP and report; do not fix outside the swept pattern.

If the pattern is regex, anchor it tightly. Prefer multiple narrow regexes over one wide one.
```

Replace the `Verification` block with:

```bash
# Residual-match check
rg --pcre2 '<REGEX>' <SCOPE_PATHS> 2>&1 | tee /tmp/<task-slug>-residual.txt
# Expected: zero matches in <SCOPE_PATHS>; matches outside scope are EXPECTED

# Tests still pass
.venv/bin/pytest --timeout 30 -q 2>&1 | tee /tmp/<task-slug>-after-pytest.log | tail -1
diff /tmp/<task-slug>-baseline-failing.txt <(grep -E 'FAILED|ERROR' /tmp/<task-slug>-after-pytest.log)
```

**Sweep tasks should explicitly state expected residuals in out-of-scope directories** so the verification grep does not false-fail on intentional non-edits.

---

## Overlay: `Role: prose-audit`

Voice-rule or corpus-grounded review and rewrite of prose. The work judges every sentence against a calibration corpus.

**Typical use cases:**

- Cover letter or resume voice-clean pass before submission
- README rewrite against project voice rules
- Public-doc audit for banned patterns (em-dash, tricolon-after-colon, theatrical mic-drops)

**Substitutions:**

Replace the `Task` section with:

```markdown
## Task

Audit `<PROSE_FILE>` against the voice rules at `<CALIBRATION_CORPUS_PATH>`. The corpus contains canonical examples of the target voice; deviations from those signals are the audit targets.

Audit dimensions:

- Lexical signals (banned-pattern grep): <LIST> (e.g., em-dashes, "not X but Y", "X: A, B, and C")
- Structural signals (per-sentence scan): <LIST> (e.g., theatrical mic-drops, passive voice in agent-erasing position)
- Coverage signals (score band): <THRESHOLD> against the canon baseline

Deliverable: a clean rewrite of `<PROSE_FILE>` that scores at or below `<BASELINE_FILE>` on `deai-scan` and `deai-check`, with no banned lexical signals.
```

Replace the `Verification` block with:

```bash
# Lexical-signal pass
python3 ~/.claude/skills/deai/deai-scan.py <PROSE_FILE> 2>&1 | tee /tmp/<task-slug>-deai-scan.txt

# Per-sentence band + family map
python3 ~/.claude/skills/deai/deai-check.py <PROSE_FILE> 2>&1 | tee /tmp/<task-slug>-deai-check.txt

# Baseline comparison (the canon Wei file for this genre)
python3 ~/.claude/skills/deai/deai-check.py <BASELINE_FILE> 2>&1 | tail -10

# Expected: target score band <= baseline score band; no banned lexical signals; no theatrical fragments at paragraph close
```

**Prose-audit tasks must voice-prime on 1-2 corpus samples before scanning.** Without a prime, the scan default reads any LLM-polished register as "clean" and the audit reports a false pass. See `wei-voice` iron rule clause 6 (the deai gate) for the full protocol.

---

## When NOT to use an overlay

Some tasks are mixed. A feature implementation that also requires a doc update is a `code` task with a follow-up `prose-audit` agent, not a single hybrid agent. Mixed roles confuse verification (which signal is canonical) and dilute scope. Split into two agents.

If the work is too small for any overlay (< 30 minutes, single-file, read-mostly), the same-tree exception in `SKILL.md` applies and the prompt is whatever is sufficient. Overlays are calibrated for batched parallel dispatch, not single-shot edits.
