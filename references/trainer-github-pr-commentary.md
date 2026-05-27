# Trainer — GitHub PR commentary (all code reviews)

Load this file whenever the trainer routes **form-check code-review** (or SDK merge codereview) and the output will appear on GitHub: PR **body**, PR **comment(s)**, or both.

**Trainer owns the shape.** form-check owns findings and tier floors; review-rigor owns scorecards. The trainer adds **Trainer notes** (gym voice) and **operator-grade test plans** on top.

---

## When this applies

- Any PR review for repos under trainer always-on policy (e.g. **buds**, **toebeans**).
- **Product PRs (default):** post via `<repo>/scripts/trainer_pr_review_post.sh`; CI gate `ci-trainer-pr-review-gate.sh`. Spec: `trainer-codereview-gate.md`.
- Manual reviews: same structure; do not route through `cursor-sdk-playground`.

**Forbidden:** findings-only tables with no teaching block; test plans or `### Manual QA` sections that only say "cold start" or "launch simulator" **without copy-paste shell** to boot the emulator, wait for `adb`/`flutter devices`, and `flutter run` / `gradlew installDebug` + `adb shell am start`; heading `### Pedagogy` or `### Cool-down` (use `### Trainer notes` only).

**Snippet helper:** `bash ~/Projects/trainer.skill/scripts/trainer_manual_test_block.sh buds|toebeans` prints the canonical emulator + launch blocks; add `--scenario <name>` for buds in-app steps when defined.

### Repo detection (buds vs toebeans) — mandatory

| PR repo | Launch block | Forbidden in Manual QA / test plan |
| ------- | ------------ | ---------------------------------- |
| **buds** | `cd ~/Projects/buds/app && flutter run …` | `./gradlew`, `:androidApp:installDebug`, `app.toebeans.android`, `~/Projects/toebeans` (shared AVD name `toebeans-pixel7` is OK) |
| **toebeans** | `cd ~/Projects/toebeans && ./gradlew :androidApp:installDebug` + `adb shell am start -n app.toebeans.android/.MainActivity` | `flutter run`, `~/Projects/buds`, `verify_buds.sh` |

- Generate snippets with `trainer_manual_test_block.sh <repo>` from that product repo’s git root; the script **errors** if the stack argument does not match the checkout.
- `trainer_pr_review_post.sh` **rejects** cross-repo launch commands before POST/PATCH.

---

## Two surfaces on GitHub

| Surface | Audience | Content |
| -------- | -------- | ------- |
| **PR body — Test plan** | Merger / QA doing hands-on checks | Granular, checkbox steps the human runs locally. Not agent shorthand. |
| **PR comment — Code review** | Reviewer + future you | Findings table + **Trainer notes** + link to test plan in body. PATCH same comment on remediate rounds (`sdk-codereview` marker). |

---

## PR body — Test plan (mandatory sections)

Use these headings in every buds/toebeans (and SDK-gated) PR:

```markdown
## Test plan

### Automated (agent / CI)

- [ ] `<exact verify command from repo root>`
- [ ] SDK trainer codereview gate (if applicable)

### Manual — prerequisites

- **Repo path:** `~/Projects/<repo>` (or active worktree path)
- **Branch:** `<branch-name>` checked out
- **Tooling:** list JDK / Flutter / Android SDK versions if non-default

### Manual — emulator cold start (required when QA needs a device)

Every manual scenario that touches the app **starts** with this block (assume **no** emulator booted). Copy from `trainer_manual_test_block.sh` or paste verbatim:

1. `export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"`
2. `flutter emulators --launch toebeans-pixel7` **or** `~/Library/Android/sdk/emulator/emulator -avd toebeans-pixel7 &`
3. Wait: `adb devices` and `flutter devices` show `emulator-5554` / `toebeans-pixel7`
4. **buds:** `cd ~/Projects/buds/app && flutter run -d emulator-5554` (or `-d toebeans-pixel7`)
5. **toebeans:** `cd ~/Projects/toebeans && ./gradlew :androidApp:installDebug` then `adb shell am start -n app.toebeans.android/.MainActivity`

Then numbered **in-app** steps (navigation, expected copy/routes).

### Manual — scenario A: <name>

Number every step after the cold-start block. Each in-app step states **where to tap / route** and **what you should see**.

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

Copy and adapt; replace bracketed placeholders. **Always** lead with the emulator cold-start block above (Android AVD `toebeans-pixel7` is the default dev device in this workspace).

```markdown
### Manual — fresh install / cold start (S13 → onboarding → garden)

**Goal:** Prove `first_run_gate_completed` and `onboarding_completed` in `app/lib/core/routing.dart` match real navigation.

#### Emulator — cold start (no device booted)

1. `export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"`
2. `flutter emulators --launch toebeans-pixel7` **or** `~/Library/Android/sdk/emulator/emulator -avd toebeans-pixel7 &`
3. Wait until ready: `adb devices` → `emulator-5554`; `flutter devices` lists the emulator
4. `cd ~/Projects/buds/app && flutter run -d emulator-5554` (or `-d toebeans-pixel7`)

#### In-app — fresh install

5. **Verify once (repo root, separate terminal):** `cd ~/Projects/buds && bash scripts/verify_buds.sh`
6. **Clean app state (required for “fresh install”):**
   - **iOS Simulator:** Long-press the Buds icon → Remove App → Delete App.
   - **Android emulator:** Settings → Apps → Buds → Storage → Clear storage (or `adb shell pm clear com.example.buds` — confirm `applicationId` in `app/android/app/build.gradle`).
7. **Relaunch** from the emulator app drawer if you cleared storage while the app was installed (or stop `flutter run` and re-run step 4).
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
<!-- head={full_sha} verdict={APPROVE|REQUEST_CHANGES|BLOCK} round={1|2} -->

## Trainer / form-check code review (round {N})

**Stakes:** {vibe-safe|vibe-careful|vibe-dangerous} · **Verdict:** {APPROVE|REQUEST_CHANGES|BLOCK}

### Findings

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| … | P0–P4 | … | fixed in `{sha}` / waived / open |

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

**Required:** paste the full **emulator cold-start** shell block (PATH → launch AVD → `adb devices` / `flutter devices` → `flutter run` or `gradlew installDebug` + `adb shell am start`), then numbered **in-app** steps with expected UI. Do **not** defer launch commands to the PR body only — reviewers must copy-paste from this section.

Minimum merge bar: cold start + scenario(s) {A, B} checked.

Snippet: `bash ~/Projects/trainer.skill/scripts/trainer_manual_test_block.sh buds|toebeans`

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

1. **Round 1:** Post comment with findings; fix all in-scope severities; push; run verify.
2. **Round 2:** Re-read full diff + call graph; PATCH comment (new `head=`, update table, refresh Trainer notes for *new* lessons); fix any new P0–P(n); push; verify.
3. **Round 3 (optional):** Repeat only if round 2 introduced regressions or verdict not APPROVE.

Update the **same** comment; do not leave a stale round-1 verdict at the top.

---

## Codereview integration

- Agent prompt: `~/Projects/trainer.skill/prompts/trainer-codereview.txt`
- Review spec: `~/Projects/trainer.skill/references/trainer-codereview.md`
- Marker: `<!-- trainer-codereview-{repo}-{branch} -->` (legacy `<!-- sdk-codereview-... -->` accepted by CI gate only for old PRs)

---

## Self-check before posting

- [ ] Manual QA / test plan uses **this PR’s repo only** (buds → Flutter; toebeans → Gradle + `app.toebeans.android`; no cross-repo paths).
- [ ] PR body test plan has emulator cold-start shell commands, numbered in-app steps, repo paths, reset/clear when needed, expected copy or routes.
- [ ] PR comment `### Manual QA` repeats the cold-start shell block (not “see PR body” only).
- [ ] PR comment has `### Trainer notes` with **Program notes**, **Your form**, **Next session** (not Pedagogy).
- [ ] Every P1+ finding has Status column or explicit waive with reason.
- [ ] Remediate round updates `head=` sha in comment meta.

---

## Mechanical enforcement (product repos)

**toebeans** ships a CI job that **fails** open PRs until the canonical comment exists with `head=` = current PR HEAD and `### Trainer notes` (forbids `### Pedagogy`):

- Gate: `scripts/ci-trainer-pr-review-gate.sh`
- Post/PATCH: `scripts/trainer_pr_review_post.sh`
- Workflow job: `Trainer PR review comment gate` in `.github/workflows/ci.yml`

**buds:** copy the same two scripts + CI job when enabling the gate there.

Descriptive rules alone do not post comments; CI blocks merge until the comment is on GitHub.
