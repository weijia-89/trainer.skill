# Trainer — GitHub PR commentary (all code reviews)

Load this file whenever the trainer routes **form-check code-review** (or SDK merge codereview) and the output will appear on GitHub: PR **body**, PR **comment(s)**, or both.

**Trainer owns the shape.** form-check owns findings and tier floors; review-rigor owns scorecards. The trainer adds **pedagogy** and **operator-grade test plans** on top.

---

## When this applies

- Any PR review for repos under trainer always-on policy (e.g. **buds**, **toebeans**).
- SDK merge gate: `_sdk_surface_codereview_to_pr.sh` posts the canonical comment; still follow this doc.
- Manual reviews: same structure even without the SDK hook.

**Forbidden:** findings-only tables with no teaching block; test plans that only say "cold start" without launch steps, repo paths, and expected UI signals.

---

## Two surfaces on GitHub

| Surface | Audience | Content |
| -------- | -------- | ------- |
| **PR body — Test plan** | Merger / QA doing hands-on checks | Granular, checkbox steps the human runs locally. Not agent shorthand. |
| **PR comment — Code review** | Reviewer + future you | Findings table + **Pedagogy** + link to test plan in body. PATCH same comment on remediate rounds (`sdk-codereview` marker). |

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

### Manual — scenario A: <name>

Number every step. Each step states **what to launch**, **where in the repo**, and **what you should see**.

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

Copy and adapt; replace bracketed placeholders.

```markdown
### Manual — fresh install / cold start (S13 → onboarding → garden)

**Goal:** Prove `first_run_gate_completed` and `onboarding_completed` in `app/lib/core/routing.dart` match real navigation.

1. **Terminal — repo root:** `cd ~/Projects/buds` (or worktree: `cd ~/Projects/buds/.worktrees/<worktree-name>`).
2. **Verify once:** `bash scripts/verify_buds.sh` (from repo root, not `app/`).
3. **Simulator or device:** Start an iOS Simulator (Xcode → Open Developer Tool → Simulator) *or* connect a physical device with USB debugging enabled.
4. **Clean app state (required for “fresh install”):**
   - **iOS Simulator:** Long-press the Buds icon → Remove App → Delete App.
   - **Android:** Settings → Apps → Buds → Storage → Clear storage (or `adb shell pm clear <applicationId>` if you know the id from `app/android/app/build.gradle`).
5. **Install and run from `app/`:**  
   `cd app && flutter run -d <device-id>`  
   (`flutter devices` lists ids; e.g. `iPhone 16`.)
6. **Expect — S13 splash (~300ms):** Full-screen “buds” wordmark + tagline. Code: `app/lib/features/onboarding/first_run_page.dart` (`_SplashView`). HTML reference: `docs/mocks/explorations/s13-first-run.html`.
7. **Expect — path question:** Copy “welcome.” and planks “new garden” / “i have a .buds file”. Privacy line at bottom. Do **not** skip; spec has no skip on this screen.
8. **Tap “new garden”.** Expect navigation to onboarding welcome: headline “a garden, not a CRM”. Code: `app/lib/features/onboarding/welcome_page.dart`.
9. **Walk onboarding** (or tap Skip on welcome/honest if testing skip path): honest → plant → how Buds works (scroll to bottom, “good, I read it”) → PII import → primary CTA to garden.
10. **Expect — garden home:** Empty or seeded garden per your DB; you must **not** bounce back to `/first-run`. Routing: `app/lib/core/routing.dart` redirect when `onboarding_completed` is true.
11. **Kill the app** (swipe away from app switcher).
12. **Relaunch Buds** from the home screen (do not reinstall).
13. **Expect — lands on garden**, not first-run or onboarding. Confirms persistence keys `first_run_gate_completed` and `onboarding_completed` in SharedPreferences (see `onboardingCompletedKey`, `firstRunGateCompletedKey` in `routing.dart`).

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

### Pedagogy (trainer)

Cap at **three** takeaways. Tie each to a finding or design choice the reader can reuse.

1. **What we were protecting:** …
2. **Pattern to remember:** … (e.g. two persisted flags → define redirect refresh + test harness overrides for each)
3. **What to watch next:** …

### Why these severities

One short paragraph: what would have broken in production or in the next PR if we had waived P1/P2.

### Round {N} remediation

- Commit(s): `{sha}` — {one-line summary}
- Verify: `{command}` → {pass|fail}

### Manual QA

Full steps are in the PR body **Test plan**. Minimum merge bar: scenarios {A, B} checked.

---

*Trainer routes form-check for findings; this comment adds teaching + links hands-on QA.*
```

### Pedagogy rules

- **Name the invariant**, not only the fix (“GoRouter does not re-run redirect unless `refreshListenable` hears notifier updates”).
- **Connect to specialist:** “form-check COR: contract between prefs keys and redirect branches.”
- **No filler praise.** Teaching is consequence + pattern + next watch, not “great job.”
- After round 2 **APPROVE**, add: “Merge when PR body manual scenarios are checked.”

---

## Remediate loop (buds P0–P4, toebeans P0–P3)

1. **Round 1:** Post comment with findings; fix all in-scope severities; push; run verify.
2. **Round 2:** Re-read full diff + call graph; PATCH comment (new `head=`, update table, add pedagogy for *new* lessons); fix any new P0–P(n); push; verify.
3. **Round 3 (optional):** Repeat only if round 2 introduced regressions or verdict not APPROVE.

Update the **same** comment; do not leave a stale round-1 verdict at the top.

---

## SDK hook integration

- `_sdk_codereview.txt` must require PR body test plan granularity before `APPROVE`.
- `_sdk_surface_codereview_to_pr.sh` embeds short verdict in body; **full** comment uses this doc’s comment template.
- Marker: prefer `<!-- trainer-codereview-... -->` alongside legacy `<!-- sdk-codereview-... -->` when both apply.

---

## Self-check before posting

- [ ] PR body test plan has numbered steps, repo paths, app launch/clear instructions, expected copy or routes.
- [ ] PR comment has **Pedagogy** section (≤3 bullets).
- [ ] Every P1+ finding has Status column or explicit waive with reason.
- [ ] Remediate round updates `head=` sha in comment meta.

---

## Mechanical enforcement (product repos)

**toebeans** ships a CI job that **fails** open PRs until the canonical comment exists with `head=` = current PR HEAD and `### Pedagogy`:

- Gate: `scripts/ci-trainer-pr-review-gate.sh`
- Post/PATCH: `scripts/trainer_pr_review_post.sh`
- Workflow job: `Trainer PR review comment gate` in `.github/workflows/ci.yml`

**buds:** copy the same two scripts + CI job when enabling the gate there.

Descriptive rules alone do not post comments; CI blocks merge until the comment is on GitHub.
