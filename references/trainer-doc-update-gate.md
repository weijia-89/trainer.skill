# Trainer  -  doc update gate (R-6 extended)

If trainer is involved in a code change and the PR targets `origin`, the PR must also update operator-facing docs. This gate applies to `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `SECURITY.md`, and any other user-facing prose.

## Why

Code without doc drift is a broken contract. The operator reads `README.md` first; if it does not match the shipped code, the operator makes wrong decisions. CHANGELOG is the only place an operator can see what changed without reading diffs. Skipping docs is not a time-saver  -  it is a deferred incident.

## Procedure

### 1. Write content first

Draft the doc changes in the same session as the code. Do not defer to "after merge."

### 2. simple-english pragmatic mode

- Short sentences (aim for 20 words or fewer).
- One verb per sentence.
- Active voice.
- No rule numbers in prose.
- Accept tricolons and hanging colons if the voice is plain.

### 3. tic for style consistency

Run `tic` (or the project's style checker) on modified docs. Fix mismatches before commit.

### 4. DEAI scan

Run the full deai skill, not just `deai-scan.py`:

```bash
python3 /Users/dubs/Projects/deai.skill/deai-scan.py <file>
```

Then load `~/Projects/deai.skill/SKILL.md` and run voice-prime, restructure, re-scan. A scan-only pass does not count.

### 5. Fix AI slop

- Replace em-dashes with " - " (space, hyphen, space).
- Convert passive constructions to active in operator-facing contexts.
- Remove latinate phrases where plain English works.
- Banned vocabulary: zero hits.

### 6. Pre-commit verification

Before staging, run the repo's actual verify commands. Examples:

```bash
# Bash syntax check (if repo has shell scripts)
find scripts -name "*.sh" -exec bash -n {} \;

# Shellcheck (if available)
if command -v shellcheck &>/dev/null; then
  find scripts -name "*.sh" -exec shellcheck {} \;
fi

# Repo-specific verification
bash scripts/verify_trainer_sync.sh   # trainer.skill only
pytest                                 # Python projects
npm test                               # Node projects
```

If any of these fail, fix before `git add`.

### 7. Operator approval

Prepare commits. Show the operator the diff. Wait for explicit approval before push.

## What counts as "user-facing docs"

| File | Always gate? | Notes |
|------|--------------|-------|
| `README.md` | Yes | First thing operators read |
| `CHANGELOG.md` | Yes | SemVer entries only |
| `ROADMAP.md` | Yes | If shipped behavior changes phase status |
| `SECURITY.md` | Yes | If scope or supported versions change |
| `docs/**/*.md` | Yes | Any public documentation |
| `references/*.md` | No | Agent-facing reference, not operator-facing |
| `specialists/*/SKILL.md` | No | Agent prompt text |

## Enforcement

This gate is procedural: the trainer checks it before approving a PR. The CI gate `trainer_pr_r6_validate.py` (Invariant 14) blocks APPROVE when code changes lack doc deltas.

## Related

- `references/trainer-codereview-gate.md`  -  R-6 harness
- `scripts/trainer_pr_r6_validate.py`  -  mechanical validator
- `README.md`  -  Authoring discipline section
