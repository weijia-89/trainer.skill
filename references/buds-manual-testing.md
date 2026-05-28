# Buds manual testing (trainer carveout)

When reviewing **`weijia-89/buds`** PRs, manual QA launch commands come from the **gitignored** buds local tree — not from toebeans Gradle paths and not from Android-first defaults meant for toebeans.

## Source of truth (local machine)

| Path | Role |
| ---- | ---- |
| `~/Projects/buds/localonly/trainer/INDEX.md` | Carveout index; policy statement |
| `~/Projects/buds/localonly/trainer/manual-testing-buds.md` | PR copy-paste blocks (marker-delimited) |
| `~/Projects/buds/localonly/process/ios-simulator.md` | **Primary** — iPhone 17 Pro UDID, cold start, erase |
| `~/Projects/buds/localonly/process/android-emulator.md` | **Optional** — AVD `buds-pixel7` (not toebeans app) |

Tracked pointer on clone: `buds/CLAUDE.md` → `localonly/trainer/INDEX.md`.

## Snippet helper

```bash
# From buds git root (preferred):
bash scripts/trainer_manual_test_block.sh
bash scripts/trainer_manual_test_block.sh --platform ios      # default
bash scripts/trainer_manual_test_block.sh --platform android
bash scripts/trainer_manual_test_block.sh --platform both

# From anywhere:
bash ~/Projects/trainer.skill/scripts/trainer_manual_test_block.sh buds [--platform ios|android|both]
```

When `manual-testing-buds.md` exists, the script prints the marked sections from that file. Otherwise it falls back to embedded iOS-first blocks in the script.

## PR comment / test plan rules

1. **Load** `INDEX.md` before writing Manual QA for a buds PR.
2. **Embed** the iOS block from `manual-testing-buds.md` (or script output `--platform ios`) at the start of every device-touching scenario.
3. Add the Android subsection only when the PR is Android-specific.
4. **Forbidden** on buds PRs: `./gradlew`, `:androidApp:installDebug`, `app.toebeans.android`, `cd ~/Projects/toebeans` as launch path.
5. AVD name **`buds-pixel7`** in buds examples; **`toebeans-pixel7`** is for toebeans only.

See also: `references/trainer-github-pr-commentary.md` (repo detection table).
