# Trainer — GitHub PR commentary (all code reviews)

Load this file whenever the trainer routes **form-check code-review** (or SDK merge codereview) and the output will appear on GitHub: PR **body**, PR **comment(s)**, or both.

**Trainer owns the shape.** form-check owns findings and tier floors; review-rigor owns scorecards. The trainer adds **Trainer notes** (gym voice) and **operator-grade test plans** on top.

---

## When this applies

- Any PR review for repos under trainer always-on policy (e.g. **buds**, **toebeans**).
- **Product PRs (default):** post via `<repo>/scripts/trainer_pr_review_post.sh`; CI gate `ci-trainer-pr-review-gate.sh`. Spec: `trainer-codereview-gate.md`.
- Manual reviews: same structure; do not route through `cursor-sdk-playground`.

**Forbidden:** findings-only tables with no teaching block; **initial PR body** test plans that say "cold start" without copy-paste setup when the PR needs device QA; trainer **remediate** comments that repeat the full launch boilerplate without a testing reason; heading `### Pedagogy` or `### Cool-down` (use `### Trainer notes` only).

**Snippet helper:** `trainer_manual_test_block.sh` — **buds:** iOS-first (`--platform ios` default); reads `~/Projects/buds/localonly/trainer/manual-testing-buds.md` when present (see `references/buds-manual-testing.md`). **toebeans:** Android Gradle block only.

### Repo detection (buds vs toebeans) — mandatory

| PR repo | Launch block | Forbidden in Manual QA / test plan |
| ------- | ------------ | ---------------------------------- |
| **buds** | **Primary:** iPhone 13 sim → `bash scripts/boot_ios_test_sim.sh` + `flutter run -d "${UDID}"` from `~/Projects/buds/app` (or `bash scripts/run_ios.sh`). **Optional:** Android AVD `buds-pixel7`. | `./gradlew`, `:androidApp:installDebug`, `app.toebeans.android`, `~/Projects/toebeans` as launch path; toebeans Gradle blocks as primary QA |
| **toebeans** | `cd ~/Projects/toebeans && ./gradlew :androidApp:installDebug` + `adb shell am start -n app.toebeans.android/.MainActivity` | `flutter run`, `~/Projects/buds`, `verify_buds.sh` |

- **buds PRs:** load `~/Projects/buds/localonly/trainer/INDEX.md`; embed iOS block from `manual-testing-buds.md` (or `bash scripts/trainer_manual_test_block.sh` from buds root).
- Generate snippets with `trainer_manual_test_block.sh <repo>` from that product repo’s git root; the script **errors** if the stack argument does not match the checkout.
- `trainer_pr_review_post.sh` **rejects** cross-repo launch commands before POST/PATCH.

### Severity remediate scope (merge bar)

| Repo | Fix or explicit waive before merge | Do not use |
| ---- | ----------------------------------- | ---------- |
| **buds** | **P0–P4** (every ranked finding) | “P0–P2 only”, “no P0–P2 blockers” without P3/P4 rows |
| **toebeans** | **P0–P3** | Same cap shorthand |

P3/P4 may be **waived** with reason and follow-up hook; they must still appear in **Bug inventory**, not omitted.

---

## Two surfaces on GitHub

| Surface | Audience | Content |
| -------- | -------- | ------- |
| **PR body — Test plan** (at **PR open**) | Merger / QA | Automated verify checkboxes; **full setup** commands (prose + inline backticks); **scenario checkboxes**. |
| **PR comment — Code review** | Reviewer + future you | **Bug inventory** + **Trainer notes**; **Manual QA** = pointer to PR body by default, shell blocks only when testing needs them. PATCH same comment on remediate rounds. |

### Default buds layout (2026-06)

**Template:** `~/Projects/trainer.skill/references/templates/buds-pr-test-surfaces.md`

| When | Shell commands |
| ---- | ---------------- |
| **PR open (body)** | Full setup once (checkout, cold start, fresh install, optional kill/relaunch) |
| **Trainer round 1** | Usually **none** — “see PR body test plan” + one-liner launch |
| **Trainer round 2+** | **Delta only** — new scenario, changed path, or targeted re-test after fix |
| **Cycle comments** | **When appropriate** — assist testing that round; no boilerplate repeat |

**Why PR body for setup:** `pr_body_validate.sh` rejects fenced bash; use labeled bullets with inline `\`commands\``. Scenario checkboxes stay `- [ ]`.

**Why not every comment:** Operator reads setup once on the PR; remediate rounds PATCH inventory/notes without duplicating cold-start blocks unless the diff changes how you test.

---

## PR body — Test plan (mandatory sections)

**buds default:** load `references/templates/buds-pr-test-surfaces.md` and adapt placeholders. **toebeans:** keep emulator Gradle block in body when lint allows, or mirror the split if a body linter is added later.

Use these headings in every buds/toebeans (and SDK-gated) PR:

```markdown
## Test plan

### Automated (agent / CI)

- [ ] `cd ~/Projects/buds && git checkout <branch>`
- [ ] `git pull --ff-only origin <branch>`
- [ ] `bash scripts/verify_buds.sh`

### Manual — setup (copy-paste at PR open)

- **Repo / branch:** `~/Projects/buds`, `<branch>`
- **Device:** iPhone 13 sim — `app/scripts/boot_ios_test_sim.sh`
- **Bundle id:** `io.github.weijia89.buds`
- **Checkout + verify:** `cd ~/Projects/buds && git checkout <branch> && git pull --ff-only origin <branch> && bash scripts/verify_buds.sh`
- **Cold start:** `cd ~/Projects/buds/app && flutter pub get && UDID="$(bash scripts/boot_ios_test_sim.sh)" && flutter run -d "${UDID}"`
- **One-liner launch:** `cd ~/Projects/buds/app && bash scripts/run_ios.sh`
- **Fresh install:** `cd ~/Projects/buds/app && UDID="$(bash scripts/boot_ios_test_sim.sh)" && xcrun simctl uninstall "${UDID}" io.github.weijia89.buds && flutter run -d "${UDID}"`

Add kill/relaunch or integration-test bullets only when this PR needs them.

### Manual — test cases

- [ ] **Scenario A (<name>):** <in-app path + expected outcome>
- [ ] **Scenario B (<name>):** …

### Sign-off

- [ ] CI green on PR HEAD
- [ ] Operator manual scenarios checked
```

### buds — PR body lint (`pr_body_validate.sh`)

- Requires `## Summary` and `## Test plan`.
- **Forbidden:** captured CI/log output; literal `\n`; fenced bash blocks with `flutter` / `bash scripts/` lines.
- **Allowed:** `- [ ] \`command\`` checklist items; `-` prerequisite bullets with inline backticks (line must not *start* with `flutter` or `bash scripts/`).

### Manual — device setup (reference)

Full blocks for **PR body at open** or **on-demand** generation — not repeated every trainer comment:

```bash
bash ~/Projects/trainer.skill/scripts/trainer_manual_test_block.sh buds --platform ios
```

**buds (optional — Android):** AVD `buds-pixel7` → `flutter run -d emulator-5554` (see `localonly/process/android-emulator.md`).

**toebeans:**

1. `export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"`
2. `flutter emulators --launch toebeans-pixel7` **or** `emulator -avd toebeans-pixel7 &`
3. Wait: `adb devices` / `flutter devices` show `emulator-5554`
4. `cd ~/Projects/toebeans && ./gradlew :androidApp:installDebug` then `adb shell am start -n app.toebeans.android/.MainActivity`

Then **in-app** steps under **Manual QA** in the trainer comment (navigation, expected copy/routes).

### Manual — test data matrix (required when scenarios need pre-seeded state)

| Scenario | State needed | Data source |
|----------|--------------|-------------|
| A: … | … | demo id / fixture / create steps below |

Load `trainer-test-data.md` for repo minimum rows. **Rule:** if a scenario needs a state demo does not provide, extend `loadDemoData`/fixtures in the same PR or document exact create steps.

### Manual — scenario A: <name>

Number every step after the cold-start block. Each in-app step states **where to tap / route** and **what you should see**. Name **data source** (e.g. `loadDemoData` → `med-luna-eye-drops` for unscheduled med).

### Manual — scenario B: <name>

...

### Manual — docs-only (if applicable)

- [ ] Open `docs/...` in browser (file URL or `open docs/.../index.html`)
- [ ] Record choice in `docs/.../DECISIONS.md`

### Sign-off

- [ ] CI green on PR
- [ ] Human merge after manual scenarios pass
```

### Flutter app template (buds-shaped)

Copy and adapt; replace bracketed placeholders. **Always** lead with the **iOS Simulator** cold-start block (`trainer_manual_test_block.sh buds` or `localonly/trainer/manual-testing-buds.md`). Add Android only when the PR is Android-specific (`--platform android`).

```markdown
### Manual — fresh install / cold start (S13 → onboarding → garden)

**Goal:** Prove `first_run_gate_completed` and `onboarding_completed` in `app/lib/core/routing.dart` match real navigation.

#### iOS Simulator — cold start (no Simulator booted)

1. Open Simulator and boot **iPhone 17 Pro** (`C2787FD6-4302-4598-89CB-5B5902AA17A5`):
   `open -a Simulator`
   `xcrun simctl boot C2787FD6-4302-4598-89CB-5B5902AA17A5`
   `xcrun simctl bootstatus C2787FD6-4302-4598-89CB-5B5902AA17A5 -b`
2. `cd ~/Projects/buds/app && flutter devices`
3. `flutter run -d C2787FD6-4302-4598-89CB-5B5902AA17A5`

#### Android emulator — optional (PR is Android-specific only)

1. `export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"`
2. `flutter emulators --launch buds-pixel7` **or** `~/Library/Android/sdk/emulator/emulator -avd buds-pixel7 &`
3. Wait until ready: `adb devices` → `emulator-5554`; `flutter devices` lists the emulator
4. `cd ~/Projects/buds/app && flutter run -d emulator-5554`

#### In-app — fresh install

5. **Verify once (repo root, separate terminal):** `cd ~/Projects/buds && bash scripts/verify_buds.sh`
6. **Clean app state (required for “fresh install”):**
   - **iOS Simulator:** Long-press the Buds icon → Remove App → Delete App (or `xcrun simctl uninstall C2787FD6-4302-4598-89CB-5B5902AA17A5 io.github.weijia89.buds`).
   - **Android emulator:** Settings → Apps → Buds → Storage → Clear storage (or `adb shell pm clear io.github.weijia_89.buds` — confirm `applicationId` in `app/android/app/build.gradle`).
7. **Relaunch** from the Simulator home screen (iOS) or emulator app drawer (Android) if you cleared storage while the app was installed (or stop `flutter run` and re-run step 3 for iOS, or step 4 for Android).
8. **Expect — S13 splash (~300ms):** Full-screen “buds” wordmark + tagline. Code: `app/lib/features/onboarding/first_run_page.dart` (`_SplashView`). HTML reference: `docs/mocks/explorations/s13-first-run.html`.
9. **Expect — path question:** Copy “welcome.” and planks “new garden” / “i have a .buds file”. Privacy line at bottom. Do **not** skip; spec has no skip on this screen.
10. **Tap “new garden”.** Expect navigation to onboarding welcome: headline “a garden, not a CRM”. Code: `app/lib/features/onboarding/welcome_page.dart`.
11. **Walk onboarding** (or tap Skip on welcome/honest if testing skip path): honest → plant → how Buds works (scroll to bottom, “good, I read it”) → PII import → primary CTA to garden.
12. **Expect — garden home:** Empty or seeded garden per your DB; you must **not** bounce back to `/first-run`. Routing: `app/lib/core/routing.dart` redirect when `onboarding_completed` is true.
13. **Kill the app** (swipe away from app switcher).
14. **Relaunch Buds** from the home screen (do not reinstall).
15. **Expect — lands on garden**, not first-run or onboarding. Confirms persistence keys `first_run_gate_completed` and `onboarding_completed` in SharedPreferences (see `onboardingCompletedKey`, `firstRunGateCompletedKey` in `routing.dart`).

### Manual — restore stub (no archive import)

1. Repeat steps 1–7 above (fresh install through path question).
2. Tap **“i have a .buds file”**.
3. **Expect — restore preview:** “your garden is intact.”, archive summary card (stub numbers). Code: `_RestorePreviewView` in `first_run_page.dart`.
4. Tap **“restore this garden”**.
5. **Expect — garden home** with **no** new people/notes from a real `.buds` file (stub only sets flags). DB must not show fake “47 people” imported.
6. **Relaunch** → still garden only.

### Manual — deep link / regression (optional)

1. With onboarding **incomplete** and first-run **incomplete**, if you can open a URL/route to `/` or `/settings`, expect redirect to `/first-run`.
2. After “new garden”, deep link to `/first-run` should redirect to `/onboarding/welcome` (gate set, onboarding not done).
```

### Android / JVM template (toebeans-shaped)

```markdown
### Manual — emulator + app launch (device QA)

#### Emulator — cold start (no device booted)

1. `export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"`
2. `flutter emulators --launch toebeans-pixel7` **or** `~/Library/Android/sdk/emulator/emulator -avd toebeans-pixel7 &`
3. Wait: `adb devices` shows `emulator-5554`; `flutter devices` lists the emulator
4. `cd ~/Projects/toebeans && ./gradlew :androidApp:installDebug`
5. `adb shell am start -n app.toebeans.android/.MainActivity`

#### In-app — <scenario name>

6. …

### Manual — docs / style lab

1. `cd ~/Projects/toebeans`
2. `./gradlew ktlintCheck detekt :shared:jvmTest`
3. Open `docs/style-lab/index.html` in a browser (`open docs/style-lab/index.html` on macOS).
4. Toggle variant packs; confirm CSS updates without console errors.
5. Read `docs/style-lab/DECISIONS.md` — do not edit “Chosen” until intentional sign-off.

### Manual — BootReceiver docs sanity (no emulator required)

1. `rg -n 'stub path|still landing|not yet wired' README.md docs/ROADMAP.md` → expect **no** stale BootReceiver claims.
2. Read `androidApp/src/main/kotlin/app/toebeans/android/notifications/BootReceiver.kt` KDoc — should describe SQLDelight rehydration, not “stub”.
```

---

## PR comment — Code review (mandatory sections)

Post **one canonical comment** per PR (PATCH on remediate). Structure:

```markdown
<!-- trainer-codereview-{repo}-{branch} -->
<!-- head={7-char-sha} verdict={APPROVE|REQUEST_CHANGES|BLOCK} round={1|2} -->

## Trainer / form-check code review (round {N})

**Stakes:** {vibe-safe|vibe-careful|vibe-dangerous} · **Verdict:** {APPROVE|REQUEST_CHANGES|BLOCK}

### Bug inventory

Declare **every** ranked defect P0–P4 from form-check (or explicit zero with evidence). Legacy heading `### Findings` is accepted by CI; prefer **Bug inventory**.

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| B-01 | P2 | … | fixed in `{sha}` / waived: … / open |

**Zero findings (example):** `No P0–P4 findings — full diff read; verify green; see Manual QA.`

**buds:** never summarize as “no P0–P2 blockers”; P3/P4 must appear here or in the zero-finding line.

### Trainer notes

Exactly three bullets (gym voice OK). Tie each to a finding or design choice.

1. **Program notes:** what we were protecting / invariant (consequence if waived).
2. **Your form:** reusable pattern from this PR (what to repeat next time).
3. **Next session:** what to watch on the next change or merge (one concrete hook).

### Why these severities

One short paragraph: what would have broken in production or in the next PR if we had waived P1/P2.

### Round {N} remediation

- Commit(s): `{sha}` — {one-line summary}
- Verify: `{command}` → {pass|fail}

### Manual QA

**Default (round 1):** point at PR body — `**Manual QA:** PR body test plan; device via \`cd ~/Projects/buds/app && bash scripts/run_ios.sh\`` (satisfies `trainer_pr_review_post.sh`).

**Add full shell blocks** only when: PR body lacks setup; new/changed test path in this round; operator needs a **delta** re-test command after a fix.

**Round 2+ remediate:** update Bug inventory + Trainer notes; keep Manual QA to one line unless the diff changes how you test.

Minimum merge bar: operator runs PR body scenarios on device when the PR touches UI/crypto/routing.

Snippet (on demand): `bash ~/Projects/trainer.skill/scripts/trainer_manual_test_block.sh buds|toebeans`

### Sign-off (automated vs manual — required in PR comment)

Separate **CI-automated** verification from **operator manual** work. Do not leave automated unchecked when the matching CI job is **SUCCESS** on current PR HEAD.

```markdown
### Sign-off

- [x] **Automated tests (CI)** — [{job name}]({link to passing Actions run on this PR HEAD}) green on `{short_sha}`
- [ ] **Manual testing** — operator: PR body scenarios (+ comment `### Manual QA` when device QA applies)
```

| Repo | CI job to link when green | Leave manual unchecked until |
| ---- | ------------------------- | ------------------------------ |
| **buds** | `Flutter analyze + test` | Operator runs PR body / comment manual steps |
| **toebeans** | `Gradle build + shared tests` | Operator runs PR body / comment manual steps |

**Agent rule:** Before POST/PATCH, read PR `statusCheckRollup` (or Actions UI). If the repo’s automated test job above is **SUCCESS** on HEAD, the automated line **must** be `[x]` with a link to that run. Never `[ ]` automated when CI already passed. Manual stays `[ ]` until the operator completes hands-on checks.

### Post-comment automated verify loop (all repos — mandatory)

Order is **not** optional:

1. **POST or PATCH** the canonical trainer comment (Bug inventory + Trainer notes; automated may start `[ ]` if not run yet).
2. **Run** the PR test plan’s automated commands from repo root (`bash scripts/smoke_test.sh`, `python3 -m unittest …`, `./gradlew …`, `flutter test`, etc.). Do not claim pass without executing.
3. **PATCH** the same canonical comment (same marker, fresh `head=`):
   - Add or update `### Automated verification` with each command `[x]` and one-line result (`PASS`, test count, short SHA).
   - Update `### Sign-off`: automated `[x]`; manual stays `[ ]`.
4. **PATCH PR body** `## Test plan` → `### Automated (agent / CI)` checkboxes to `[x]` when step 2 passed (use `gh pr edit`).

Skill/script repos without a device QA gate (e.g. **opacite**): local automated run + CI link satisfies the automated sign-off; manual remains operator-owned.

**Forbidden:** APPROVE comment with automated lines still `[ ]` after you had time to run the repo verify commands in-session.

---

*Trainer routes form-check for findings; this comment adds teaching + links hands-on QA.*
```

### Trainer notes rules

- **Name the invariant**, not only the fix (“GoRouter does not re-run redirect unless `refreshListenable` hears notifier updates”).
- **Connect to specialist:** “form-check COR: contract between prefs keys and redirect branches.”
- **No filler praise.** Notes are consequence + pattern + next watch, not “great job.”
- **Never** use `### Pedagogy` or `### Cool-down` as the section heading.
- After round 2 **APPROVE**, add: “Merge when PR body manual scenarios are checked.”

---

## Remediate loop (buds P0–P4, toebeans P0–P3)

1. **Round 1:** Post comment with findings; PR body already has setup commands; Manual QA pointer unless body is incomplete.
2. **Round 2:** Re-read full diff; PATCH comment (new `head=`, update table, refresh Trainer notes); add Manual QA shell **only if** test path changed; push; verify.
3. **Round 3 (optional):** Same — no boilerplate shell repeat.

Update the **same** comment; do not leave a stale round-1 verdict at the top.

---

## Codereview integration

- Agent prompt: `~/Projects/trainer.skill/prompts/trainer-codereview.txt`
- Review spec: `~/Projects/trainer.skill/references/trainer-codereview.md`
- Marker: `<!-- trainer-codereview-{repo}-{branch} -->` (legacy `<!-- sdk-codereview-... -->` accepted by CI gate only for old PRs)

---

## Self-check before posting

- [ ] Manual QA / test plan uses **this PR’s repo only** (buds → Flutter + `boot_ios_test_sim.sh`; toebeans → Gradle + `app.toebeans.android`; no cross-repo paths).
- [ ] **buds PR body (at open):** setup commands + scenario checkboxes; no fenced bash blocks (`pr_body_validate.sh`).
- [ ] **Trainer comment Manual QA:** PR body pointer by default; shell blocks only when testing needs them (not full boilerplate every PATCH).
- [ ] **Test data matrix:** each scenario maps to seed id, fixture, or documented create steps (`trainer-test-data.md`).
- [ ] PR comment has `### Trainer notes` with **Program notes**, **Your form**, **Next session** (not Pedagogy).
- [ ] **Bug inventory** lists every P0–P4 (or explicit `No P0–P4 findings` with evidence); buds has no P0–P2-only cap language.
- [ ] Every P1+ row has Status `fixed` / `waived` / `open` (open P3/P4 on buds needs waive reason before APPROVE).
- [ ] Remediate round updates `head=` sha in comment meta.
- [ ] Post-comment loop done: automated commands **run** in-session, then comment `### Automated verification` + `### Sign-off` automated `[x]` PATCHed; PR body automated boxes checked.
- [ ] PR comment `### Sign-off`: automated line `[x]` with local result and/or CI run link on HEAD; manual `[ ]` until operator sign-off.
- [ ] Export delta: obligation **B** closed in declared contract surfaces, or Bug inventory **waive** row with Status, reason, and **file list** of unchecked surfaces (toebeans P0–P3; buds P0–P4).
- [ ] No APPROVE on export delta with silent B skip (no closure, no waive row).

### Export-delta B waiver row (Bug inventory)

When waiving contract-surface closure, add a row (severity per repo tier):

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| B-CS | P3 | Contract-surface B waived: `{old_symbol}` — surfaces not checked: `AGENTS.md`, `scripts/foo.sh` | waived: {reason}; follow-up {hook} |

---

## Mechanical enforcement (product repos)

**toebeans** ships a CI job that **fails** open PRs until the canonical comment exists with `head=` = current PR HEAD and `### Trainer notes` (forbids `### Pedagogy`):

- Gate: `scripts/ci-trainer-pr-review-gate.sh`
- Post/PATCH: `scripts/trainer_pr_review_post.sh` — **never** `gh pr comment` for canonical trainer reviews (bypasses marker PATCH + spawns duplicate comments).
- Workflow job: `Trainer PR review comment gate` in `.github/workflows/ci.yml`

**buds:** copy the same two scripts + CI job when enabling the gate there.

Descriptive rules alone do not post comments; CI blocks merge until the comment is on GitHub.
