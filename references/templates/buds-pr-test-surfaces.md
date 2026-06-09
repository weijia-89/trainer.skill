# Buds PR test surfaces — default template (trainer)

Use on **PR open** (body) and in **review comments** only when testing needs help. Validated against `buds/scripts/pr_body_validate.sh` (PR body) and `trainer_pr_review_post.sh` (trainer comment).

**Rule:** Full copy-paste setup lives in the **initial PR body** once. Trainer canonical comments and cycle comments repeat shell **only when appropriate** (see below).

Canonical path: `~/Projects/trainer.skill/references/templates/buds-pr-test-surfaces.md`

---

## When to include shell commands

| Surface | Shell blocks |
| ------- | ------------- |
| **PR body** (at open) | **Yes** — full setup under Manual — prerequisites / setup |
| **Trainer comment round 1** | **No** by default — point at PR body; add blocks only if body is missing setup |
| **Trainer comment round 2+** | **Only when needed** — new scenario, changed launch path, fix needs targeted re-test |
| **Cycle / review comments** | **Only when needed** — assist operator testing that round (e.g. CI fix → “re-run verify”) |

`trainer_pr_review_post.sh` still requires `~/Projects/buds` and `flutter run` in the canonical comment — a one-liner pointer is enough on remediate rounds.

---

## PR body — paste at PR open

Replace `{branch}`, scenario text, and CI links.

### Automated (agent / CI)

- [ ] `cd ~/Projects/buds && git checkout {branch}`
- [ ] `git pull --ff-only origin {branch}`
- [ ] `bash scripts/verify_buds.sh`

### Manual — setup (copy-paste once here)

- **Repo / branch:** `~/Projects/buds`, `{branch}`
- **Device:** iPhone 13 sim (`app/scripts/boot_ios_test_sim.sh`; creates `buds-iPhone-13` if missing)
- **Bundle id:** `io.github.weijia89.buds`
- **Checkout + verify:** `cd ~/Projects/buds && git checkout {branch} && git pull --ff-only origin {branch} && bash scripts/verify_buds.sh`
- **Cold start:** `cd ~/Projects/buds/app && flutter pub get && UDID="$(bash scripts/boot_ios_test_sim.sh)" && flutter run -d "${UDID}"`
- **One-liner launch:** `cd ~/Projects/buds/app && bash scripts/run_ios.sh`
- **Fresh install:** `cd ~/Projects/buds/app && UDID="$(bash scripts/boot_ios_test_sim.sh)" && xcrun simctl uninstall "${UDID}" io.github.weijia89.buds && flutter run -d "${UDID}"`

Add optional bullets only when this PR needs them (kill/relaunch, integration test command, Android AVD).

### Manual — test cases

- [ ] **Scenario A ({name}):** {in-app path + expected outcome}
- [ ] **Scenario B ({name}):** …

### Sign-off

- [ ] CI green on PR HEAD
- [ ] Operator manual scenarios checked

### PR body lint (`pr_body_validate.sh`)

- Do **not** use fenced bash blocks — lines inside still fail lint.
- Put each command in a `-` bullet with inline backticks; line must not *start* with `flutter` or `bash scripts/` (prefix with label text).
- Scenario rows use `- [ ]` checkboxes; do **not** checkbox every setup command.

---

## Trainer comment — round 1 (default)

Under **Trainer notes** → **Manual QA** (minimal):

```markdown
**Manual QA:** PR body test plan — run setup once, then check scenarios A/B. Device: `cd ~/Projects/buds/app && bash scripts/run_ios.sh`
```

Add full shell blocks in the comment **only if** the PR body has no device setup (catch-up) or the PR is docs/CI-only with no body test plan.

---

## Trainer comment — round 2+ (remediate)

PATCH Bug inventory + Trainer notes. **Manual QA** section:

- **Default:** one line — what to re-test + pointer to PR body (`Merge when PR body scenarios checked`).
- **Add shell** when: new manual scenario landed; launch/uninstall path changed; operator needs a delta command (e.g. after crypto fix: fresh install + unlock scenario only).

Example delta block:

```markdown
**Manual QA (delta @ {sha}):** fresh install, then Scenario B only — `xcrun simctl uninstall "${UDID}" io.github.weijia89.buds` …
```

---

## Cycle / review comments (non-canonical)

Use for round-specific notes (e.g. “cycle 4 — CI analyze fix”). Include commands **only** when they help test that cycle’s change — not the full cold-start boilerplate.

Generate fresh blocks when needed:

    bash ~/Projects/trainer.skill/scripts/trainer_manual_test_block.sh buds --platform ios
