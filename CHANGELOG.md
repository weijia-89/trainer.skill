# Changelog

All notable changes to the `trainer` skill will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/) with the rules below.

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; the specialist gym-skills list gains or loses entries; teaching-responsibility tier semantics change.
- **MINOR**: new sync target added; a specialist gym-skill's invocation pattern is updated; new section added without changing existing semantics.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

## [Unreleased]

### Added

- **`specialists/form-check/tools/generation_gate.sh`** — executable, validates new/modified bash scripts for generation-time safety. Checks: `set -euo pipefail` header, no env var collisions (LANG, LC_ALL, PATH, HOME), numeric arg validation, tool existence checks, test co-existence, shellcheck (if available), safe-terminal compliance (no heredocs outside usage/help, no `cd &&` chains). Spirit-over-letter: warns on missing tests/tool checks in default mode, fails in `--strict` mode. Bypass: `GENERATION_GATE_BYPASS=1` (logged to `.recovery/calibration.jsonl`).
- **`specialists/form-check/tests/test_generation_gate.sh`** — 10 tests: help, bypass, missing header, LANG collision, clean script, heredoc outside usage (fail), heredoc in usage (pass), cd && chain (fail), SCRIPT_DIR pattern (pass), no test file warning-only.
- **`specialists/form-check/templates/pre-commit-combined`** — merged pre-commit hook running both generation gate (for .sh files) and LLM-code gate (for LLM-generated files). Single hook, fail-closed, deduplicated from separate hooks.
- **`.github/workflows/trainer-pr-review-gate.yml`** — added parallel `generation-gate` job. Runs on PRs modifying `.sh` files. Installs shellcheck, runs generation gate with `--strict`.
- **`specialists/form-check/tools/llm_code_gate.sh`** — executable, language-agnostic gate runner. Auto-detects language from file extensions. Runs 4 layers: structural/graph, type/compile, execution/tests, lint/format. Supports `--max-iter N` (default 3), `--strict`, `--lang`. Exit codes: 0=pass, 1=fail, 2=config error, 3=max iterations exceeded. Tamper-isolated: runs in subshell, does not modify source files.
- **`specialists/form-check/templates/pre-commit-llm-gate`** — Git pre-commit hook template. Copies to `.git/hooks/pre-commit` to block commits until gate passes. Fail-closed by design. Supports `LLM_GATE_ALL=1` to gate every commit, or auto-detects files marked `# llm-generated`.
- **`specialists/form-check/templates/llm_code_gate_ci.yml`** — GitHub Actions CI workflow template. Runs the 4-layer gate on push and PR. Matrix strategy for python/go/typescript/rust. Fails the build if any layer fails.
- **`specialists/form-check/templates/pyright_strict.json`** — pyright strict configuration for LLM-generated Python. Enables all strict checks including `reportMissingImports`, `reportMissingTypeStubs`, `reportUntypedFunctionDecorator`, `reportUnknownParameterType`. This is the config referenced by A-3 in the S4 canon.
- **`specialists/form-check/templates/Makefile.llm-gate`** — Makefile targets for `make gate`, `make gate-strict`, `make gate-python`, etc. Convenience wrapper around `llm_code_gate.sh`.
- **`specialists/form-check/references/llm_code_correctness_gate.md`** — language-agnostic mechanical gate for LLM-generated code, integrating Piranesi S4 research (0729-trainer-language-enforcement). Four-layer gate: structural/graph checks, type/compile layer, execution/functional layer, runtime schema validation. Gate-ON default with human-approved skip as exception. Domain-conditional language guidance (web→TypeScript, ML→type-checked Python, servers→Go, perf→Rust) without language mandate. See R-7 below.
- **`specialists/form-check/templates/structural_semantic_trigger.md`** — structural-vs-semantic decision axis for when the gate applies. Structural tasks (decidable from bytes: format, presence, count, schema) get the heavy gate; semantic tasks (requires meaning: quality, similarity, architectural fit) get light gate or human review. Worked example included.
- **`scripts/reviewer_surface_tracker.py`** — per-pass surface manifest tracker for the autonomous code-review loop; gates each pass on novelty (≥50% previously-unseen surface) so the stop condition is not reachable by re-trace. Stdlib only, read-only under `--check`.
- **`scripts/test_reviewer_surface_tracker.py`** — 7 tests: novelty threshold pass/fail, empty-surface rejection (no div-by-zero), idempotent check, CLI arg parsing, manifest roundtrip.
- **`specialists/cruft/`** — new specialist: tags session/scratchpad artifacts with the `.cruft.md` slug + a `# META:` purpose/date header (the staleness assessment made explicit); defines the deterministic cleanup convention and its iron law (no deletion unless the adversarial-review gate is GREEN AND a PR merges or the session closes).
- **`scripts/prune_cruft.sh`** — deterministic `*.cruft.md` cleanup. Refuses deletion unless the review gate is GREEN (`.trainer/reviews-complete` sentinel OR `verify_trainer_codereview.sh` exits 0) or `--force-after-review` is passed; scans by suffix only; handles any filename safely (`-print0` + array); never prunes inside trainer.skill.
- **`.github/PULL_REQUEST_TEMPLATE.md`** — PR body template enforcing Summary, Changes, Test plan, and Notes on every PR. Test plan is required even if the answer is "None"; no empty test plans allowed.
- **`specialists/spotter/`** — new specialist for CI/CD failure diagnosis and fixing. Covers bash syntax, shellcheck, generation gate, verify script, workflow YAML, and missing permission failures. Includes `references/ci-fix-patterns.md` with signature-to-fix catalog and pre-flight checklist.
- **`references/trainer-doc-update-gate.md`** — procedural gate requiring CHANGELOG.md, README.md, and user-facing docs updates in every trainer-involved PR. Enforces simple-english pragmatic mode, full deai skill (not scan-only), AI slop cleanup, and pre-commit verification (`bash -n`, `shellcheck`, `python3 -m json.tool`). Operator approval required before push.
- **`references/templates/trainer-pr-comment-template.md`** — generic PR comment template for autonomous code review rounds. Includes Bug inventory, Trainer notes, remediation, Manual QA pointer, and Sign-off sections.
- **`scripts/lib/trainer_codereview_contract.py`** — mechanical enforcement of the review output style rule: `FORBIDDEN_REVIEW_METHODOLOGY` rejects PR comments that disclose review methodology, posture, or check counts ("multi-posture", "personas", "postures", "loop 1", "loop 2", "150 checks", "75 checks", "5 personas"). Wired into `validate_review_comment`, so it applies to every repo the trainer gate validates.
- **`tests/trainer_codereview/fixtures/methodology_disclosure_bad.md`** + contract unit tests — negative fixture and per-term coverage for the review output style enforcement.
- **`scripts/verify_autonomous_code_review.py`** — output style rule presence + parity guard: both `trainer-codereview.md` and `trainer-github-pr-commentary.md` must carry the `Review output style` rule and the parity marker, so silent deletion or drift in either surface fails the contract gate (Invariant 12). Guard unit tests added in `tests/trainer_routing/`.

### Changed

- **`references/trainer-github-pr-commentary.md`** — new mandatory `### Review output style` rule before the PR comment template: PR comments must never mention "multi-posture", "personas", "postures", "loop 1", "loop 2", "150 checks", "75 checks", "5 personas", or any review process/methodology description; never describe how the review was conducted or how many checks were run. Output limited to Bug inventory + Trainer notes + Automated verification + Sign-off. Rule sits outside the copy-paste template fence so it is not posted as a comment section.
- **`references/trainer-codereview.md`** — GitHub surfaces bullet mirrors the review output style rule and cross-references `trainer-github-pr-commentary.md` § Review output style.
- **`specialists/form-check/references/notes.md`** — added 15 PIRANESI citation tags bridging Piranesi S4 claim IDs to trainer citation hygiene. Tiers: T1-verified for arXiv papers (2601.12146, 2512.18131, 2606.21619, 2607.08981-class), T2-secondary for incident trackers and single-author drafts.
- **`specialists/form-check/checklists/INDEX.md`** — decision tree now routes LLM/agent touches to `references/llm_code_correctness_gate.md` and `templates/structural_semantic_trigger.md` alongside existing `owasp_llm_top10.md`.
- **`specialists/form-check/checklists/bug_class_audit.md`** — § B (AI-PR-specific bug shapes) extended with 7 LLM-specific bug classes: plausible-completion trap (26.2% base-pass/extension-fail), reward-hacking (30.4% of SWE tasks), skill-instruction droppability (117 violations/day), type-checker bypass (97% evasion rate), circular self-validation, schema failure at boundary (10–20%), cross-file/config incoherence.
- **`specialists/form-check/checklists/preflight_10q.md`** — Q7 (LLM contract) now includes: "If LLM-generated code: is there a mechanical correctness gate?"
- **`specialists/form-check/multi-language/go.md`** — added anti-fixation clause: "This file is tooling guidance, not a mandate. Trainer does not enforce any single language."
- **`specialists/form-check/multi-language/rust.md`** — added identical anti-fixation clause.
- **`specialists/form-check/rubrics/confidence_score.md`** — Component 2 (Test verification, weight 20): full credit now requires "mechanical correctness gate passed for LLM-generated code"; half credit for "gate skipped without justification". Component 4 (Bug-class coverage, weight 12): full credit now requires "LLM-specific bug classes for LLM-generated code".
- **`specialists/form-check/rubrics/stack_decision.md`** — reconciled with anti-fixation: Go is "common but not mandated" for CLIs; Python strict-type checking (mypy/pyright) is mandatory for LLM-generated Python.
- **`references/trainer-autonomous-code-review.md`** — Review loop now requires the surface tracker `--record`/`--check` each pass; stop condition redefined to terminate only on `unexplored == 0` OR two consecutive passes each satisfying novelty ≥ 50% + zero findings + all verify exit 0; Forbidden list extended to bar passes that skip `--check` and STOP claims without tracker evidence.
- **`specialists/pr/SKILL.md`** — composed the new `cruft` specialist; added **§8 Post-merge cruft cleanup**: after a PR merges and the review gate is GREEN, writes `.trainer/reviews-complete` then runs `prune_cruft.sh --apply`; documents the session-close variant (superset of the request-cap R4c webfetch-cache cleanup for `.cruft.md` scratchpads).

### R-7 (LLM-code correctness gate integration)

Research question: should trainer enforce/coach strongly-typed languages (Go, Rust, Java, C#) over Python for LLM-generated scripting to reduce silent-bug surface? Piranesi S1→S4 extended pipeline investigated. Verdict: **reject typed-language mandate**; adopt language-agnostic mechanical gate. Evidence: type checkers catch only ~3% of LLM structural failures (arXiv 2607.08981-class); typed languages raise LLM compile-error rate, not lower it (arXiv 2512.18131); dominant failure class is semantic/functional and language-agnostic; token cost premium ~1.45–1.77x vs Python. The gate fixes compilation (necessary) but not semantics (not sufficient). All findings documented in `llm_code_correctness_gate.md` with 4 falsifiers (what would flip the verdict).

### R-6

- Autonomous code-review loop logic violation closed: spec previously trusted self-reported exploration with no mechanical novelty gate; the tracker enforces ≥50% new exploration per pass before a STOP can be claimed.

### Fixed

- **`specialists/form-check/tools/llm_code_gate.sh`** — fixed broken iteration logic (`iter` never incremented because `exit 1` preceded it); extracted inline `python3 -c` to external `check_python_imports.py` (safe-terminal Tier-1 #5 compliance); added `--lang` validation (rejects unsupported languages with clear error).
- **`specialists/form-check/tools/generation_gate.sh`** — replaced `mapfile -t` with portable `while IFS= read -r` loop for bash 3.2 (macOS default); added secret detection (AWS keys, tokens, passwords) with self-flagging protection; added test quality check (minimum 3 assertions); added bypass justification requirement (`GENERATION_GATE_JUSTIFICATION`); added emergency disable (`GENERATION_GATE_EMERGENCY_DISABLE=1`); set restrictive log permissions (`chmod 600` on `.recovery/calibration.jsonl`); fixed quote-escaping bugs in secret pattern matching.
- **`specialists/form-check/templates/pre-commit-combined`** — fixed command injection via filename: `$SH_FILES` now passed as properly quoted array instead of word-split string.
- **`specialists/form-check/templates/Makefile.llm-gate`** — auto-discovers gate script via `command -v` instead of hardcoded `$(HOME)/Projects/trainer.skill/...` path.
- **`.github/workflows/trainer-pr-review-gate.yml`** — pinned `actions/checkout` to commit SHA (`11bd71901bbe5b1630ceea73d27597364c9af683`); added `concurrency` group to prevent redundant concurrent jobs; added parallel `generation-gate` job with shellcheck installation.
- **`references/operator-path-output.md`** — scrubbed the operator's real private project name from all example paths; replaced with the neutral placeholder `~/Projects/<project>/`. The private-path leak scanner (`verify_trainer_sync.sh` CI repo-only checks) flags real private project layouts in tracked files, so a public reference doc must not embed the real path. Verified: `GITHUB_ACTIONS=true ... verify_trainer_sync.sh` now returns `VERDICT: PASS`. (Separate from the cruft-specialist PR; kept focused per single-concern branch discipline.)
- **`scripts/prune_cruft.sh`** — corrected `TRAINER_ROOT` path resolution: `dirname(BASH_SOURCE)/../..` overshot to `/Users/dubs/Projects` (prefix of every sibling repo), so the self-guard refused to prune cruft in any repo other than `trainer.skill`. Now resolves `SCRIPT_DIR` to an absolute path and steps up one level (one level, not two) to get the correct `trainer.skill` root. Found during session-close use on the toren repo.

## [0.15.1] — 2026-07-01

### Added

- **`references/trainer-implementation-babysitter.md`** — plan-row gate loop (H1–H7) for ChatPRD implementation execution; pairs with piranesi PIR-26 handoff.
- **`scripts/verify_phase11_synthesis_gates.sh`** — offline WP-0..WP-5 falsifier bundle from S4e synthesis plan (live blind audit operator-opt-in).

### Fixed

- **`tests/context_budget/budget.toml`** — snapshot drift after SKILL footer references (Inv context budget).

### Verified (offline synthesis close-out)

- Layer C `mutation_test_skill.py` — no load-bearing section drops at trainer N.
- `verify_phase11_synthesis_gates.sh` — VERDICT PASS (offline).

## [0.15.0] — 2026-07-01

### Added

- **Phase 11 Layer A driver** — `scripts/run.sh` (`--k` pass-rate stability, RULE #4 isolation), `scripts/harness_adapters/anthropic_opus.py` (dated snapshot fails closed; USER-DATA fence), `scripts/phase11_report.py`, `scripts/calibration_analyze.py` (Layer B honest-empty), `scripts/mutation_test_skill.py` (Layer C tiny-N), `scripts/verify_phase11_isolation.sh`, `tests/scenarios/harness/_repro.py`, `Transcript.with_floor()` in `tests/scenarios/harness/_grading.py`.
- **Invariants 15–16** in `scripts/verify_trainer_sync.sh` — scenario reference self-pass; committed run meta reproducibility.
- **CI smoke** — offline `run.sh` + `summary.txt` existence in `python-package-conda.yml`.

### Changed

- **`README.md`**, **`tests/scenarios/README.md`**, **`ROADMAP.md`** — honest-scope: falsifiability suite for a named dated model, not measured behavioral delta.
- **`SKILL.md` v0.15.0** — version bump only; routing unchanged.

## [0.14.0] — 2026-06-28

### Added

- **`references/trainer-autonomous-code-review.md`** — default **code review** loop (explore → trace → test → fix until two clean passes). Operator trigger is **code review**, not a separate phrase.
- **`scripts/verify_autonomous_code_review.py`** — Invariant 12: routes code review to form-check `file_read` + `code-review`; rejects `autonomous code review` as operator trigger text.
- **Invariant 13 anti-theater harness** — `scripts/lib/trainer_codereview_contract.py`, `trainer_review_comment_validate.py`, `trainer_pr_body_validate.py`, `scripts/verify_trainer_codereview.sh`, `tests/trainer_codereview/fixtures/round1_theater_bad.md`, `.github/workflows/trainer-pr-review-gate.yml`.
- **User-facing docs gate (R-6)** in `trainer-codereview.md` / `trainer-codereview-gate.md` — when a PR touches `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `SECURITY.md`, or other operator prose, agent runs the **full deai skill** (voice-prime → restructure → re-scan), not `deai-scan.py` alone.

### Changed

- **`SKILL.md` v0.14.0** — code review / PR review routes to `trainer-codereview.md` + loop doc + form-check `code-review`; Invariants 12–13 in verify footer.
- **`references/trainer-codereview.md`**, **`prompts/trainer-codereview.txt`** — default loop doc; R-6 user-facing docs + deai.
- **`references/workflow-skill-router.md`** — single code-review row; verify `verify_trainer_codereview.sh`.
- **`scripts/trainer_pr_review_post.sh`** — strip pasted HTML markers before prepend; validate assembled body; PATCH oldest canonical comment and delete marker duplicates; forbid `gh pr comment` for trainer reviews (`trainer-github-pr-commentary.md`).
- **`scripts/verify_trainer_sync.sh`** — Invariant 12 (code-review loop) + Invariant 13 (anti-theater).
- **`README.md`**, **`ROADMAP.md`**, **`SECURITY.md`** — v0.14.0 line, code-review harness layout, supported version table.

### Fixed

- Round-1 theater APPROVE on PR #20 (placeholder Bug inventory + grep-only verify) is now a failing fixture in CI.
- Duplicate trainer PR comments from raw `gh pr comment` bypass; duplicate HTML markers that could collapse the GitHub UI.
- **Invariant 14 (R-6 harness):** `trainer_pr_r6_validate.py` + CI gate block APPROVE when operator-facing code changes lack doc deltas or R-6 closure in the canonical comment.

## [0.13.0] — 2026-06-05

### Added

- **`references/trainer-epistemic-layers.md`** — L1/L2/L3 epistemic routing (research vs trace QA vs structured truth); §TRIGGER load gate; TR-1 primary-layer rule; E-T1/E-T2/E-T3 eval-corpus implementation plan (trainer/form-check, not Palamedes); coached pushback triggers; cross-links to palamedes eval literacy + architecture.

### Changed

- **`SKILL.md` v0.13.0** — integrations paragraph + routing-flow step for epistemic layer mix; references table row.
- **`scripts/verify_trainer_sync.sh`** — `trainer-epistemic-layers.md` in CI required gate files; portable tracked-file collection (replaces `mapfile` for macOS bash 3.2).
- **`mirrors/windsurf-trainer.md`**, **`.cursor/rules/trainer.mdc`** — version pointer 0.13.0 (Projects tree; sync via `verify_trainer_sync.sh`).

## [0.12.0] — 2026-05-25

### Added

- **`references/templates/buds-pr-test-surfaces.md`** — setup on **initial PR body**; trainer/cycle comments include shell only when testing needs it.
- Tracked mirror: `buds/docs/trainer/pr-test-plan-template.md`.
- **`references/trainer-contract-surfaces.md`** — export delta gate; obligations A (diff-primary), B (contract-surface closure in declared surfaces only), C (verify via Inputs row); routing step 3 in `trainer-codereview.md` and `prompts/trainer-codereview.txt`.
- **`references/trainer-github-pr-commentary.md`** — mandatory PR body test-plan granularity and PR comment **`### Trainer notes`** (Program notes · Your form · Next session); forbids Pedagogy heading.
- **`references/trainer-codereview.md`**, **`references/trainer-codereview-gate.md`**, **`prompts/trainer-codereview.txt`** — canonical PR review (migrated off `cursor-sdk-playground`).
- **`scripts/ci-trainer-pr-review-gate.sh`**, **`scripts/trainer_pr_review_post.sh`**, **`scripts/trainer_pr_review_gate_rerun.sh`**, **`scripts/test_ci_trainer_pr_review_gate.sh`**, **`scripts/test_trainer_pr_review_gate_rerun.sh`** — canonical mechanical PR review gate + idempotent gate job rerun after POST/PATCH (copy into product repos).

### Fixed

- **`references/trainer-github-pr-commentary.md`** — comment meta `head=` template aligned to `{7-char-sha}` (matches `trainer_pr_review_post.sh` and `ci-trainer-pr-review-gate.sh`; was `{full_sha}`).
- **`references/trainer-github-pr-commentary.md`** — buds Flutter template example leads with iOS Simulator cold-start (Android block optional); matches iOS-first prose and `trainer_manual_test_block.sh`.
- **`prompts/trainer-codereview.txt`** — Task steps label obligations A/B/C; obligation B waive row requirements; review-rigor scorecard step; Forbidden mirrors `trainer-codereview.md` (export-delta B, review-rigor P1/P2, launch-shell test plans).
- **`references/trainer-contract-surfaces.md`** — typo `undecared` → `undeclared`.
- **`scripts/verify_trainer_sync.sh`** — dangling-`~/.cursor` troubleshooting note; early fail with repo-only fallback hint; CI repo-only path checks `prompts/trainer-codereview.txt` presence.

### Changed

- **`references/trainer-github-pr-commentary.md`** — PR-body-first layout; iPhone 13 via `boot_ios_test_sim.sh`; no full boilerplate on every remediate PATCH.
- **`scripts/trainer_manual_test_block.sh`** — buds iOS fallback uses script-based iPhone 13 blocks.
- **`references/buds-manual-testing.md`**, **`prompts/trainer-codereview.txt`**, **`SKILL.md`** — PR-body-first, comment-on-demand.
- **Integrations routing** — mechanical MCP wireups point to `@wintermute` (`~/Projects/wintermute.skill/SKILL.md`); replaces retired `CURSOR_INTEGRATIONS_GUIDE.md`.
- **Playground decoupling** — product PR codereview no longer references `cursor-sdk-playground` scripts or `_sdk_codereview.txt`.
- **`SKILL.md` v0.12.0** — new § GitHub PR commentary; form-check adversarial-review clarifies trainer owns GitHub surfaces.
- **`specialists/form-check/SKILL.md`** — synthesis points to trainer-github-pr-commentary for PR output.
- **`references/sdk-merge-codereview-gate.md`** — retired stub; use `trainer-codereview-gate.md` instead.
- **`.cursor/rules/trainer.mdc`** — v0.12.0 pointer + PR commentary load rule.

### Added (prior)

- **`SECURITY.md`** — private GitHub advisory reporting, supported versions, explicit scope (documentation skill bundle, not a runtime product), no secrets in public issues.
- **`docs/BRANCH_PROTECTION.md`** — policy table, solo-maintainer tradeoffs, `gh api` inspect and apply commands for `main`.
- **`scripts/apply_branch_protection.sh`** — idempotent branch protection PUT; `DRY_RUN=1` by default; set `GH_REPO=weijia-89/trainer.skill` before apply.
- **`scripts/verify_github_hardening.sh`** — layout checks plus `apply_branch_protection.sh` dry-run smoke (catches script regressions verify-only file tests miss).

### Changed

- **`README.md`** — merged with `main` webapp update (#2); retains Security section and hardening layout entries.
- **`scripts/apply_branch_protection.sh`**, **`scripts/verify_github_hardening.sh`**, **`SECURITY.md`**, **`docs/BRANCH_PROTECTION.md`** — sdk-review comment cleanup (round 2).

### Fixed

- SDK codereview round 2: playground `trainer_github_hardening.sh` VERIFY uses `./scripts/verify_github_hardening.sh` (F4).

## [0.11.0] (2026-05-25): Context compactness P2/P3/P5 — compact router + on-demand references

**MINOR per SemVer rules.** Root `SKILL.md` becomes a route-and-gate router (~141 lines, ~2089 est tokens; includes F2 `file_read` overlays). Operational depth moves to on-demand reference files; routing semantics and coaching stance unchanged.

### Added

- **`references/trainer-runtime-compactness.md`** — communication discipline, decision-presentation template, rationalizations table, proactive teaching depth, worked examples, bundle/sync note (P2 lazy-load target).
- **`references/trainer-pre-action-gates.md`** — mechanical pre-action three-facts gate, triggers, adversarial-review pass (P3 cross-reference; trainer-owned overlay).
- **`references/trainer-dispatch-gates.md`** — dispatch-before-dispatch manifest procedure, three-layer architecture, status-check closeout (P5 cross-reference; trainer-owned overlay).
- **`tests/context_budget/`** — `budget.toml`, `check_context_budget.py` (warn-only gate), `measure_context.py`, README.

### Changed

- **`SKILL.md`** — compressed from 324 to 141 lines; adds on-demand reference map; version 0.10.1 → 0.11.0; mandatory `file_read` overlays anchored to `~/Projects/trainer.skill/references/` ([PR #6](https://github.com/weijia-89/trainer.skill/pull/6), Invariant 1b).
- **`scripts/verify_trainer_sync.sh`** — Invariant 5 comment updated for v0.11.0 compact router; **Invariant 11** added (CI + local `check_context_budget.py` hook); `references/` Claude mirror sync ([PR #6](https://github.com/weijia-89/trainer.skill/pull/6), Invariant 1b).
- **`~/trainer.skill`** clone layout — existing clones must move or symlink to `~/Projects/trainer.skill` (`mv ~/trainer.skill ~/Projects/trainer.skill` or `ln -sf ~/Projects/trainer.skill ~/trainer.skill`); re-run **`scripts/verify_trainer_sync.sh`** so absolute overlay paths and Claude **`references/`** mirror resolve ([PR #6](https://github.com/weijia-89/trainer.skill/pull/6)).

### Verification

- `bash scripts/verify_trainer_sync.sh` → PASS
- `python3 tests/context_budget/check_context_budget.py` → PASS (VERDICT=PASS, warn-only)
- `python3 tests/context_budget/test_check_context_budget.py` → PASS (7/7 unit tests)

## [0.10.2] (2026-05-23): Bundle superset v0.8.5 closeout roadmap alignment

**PATCH per SemVer rules.** Bundles `superset` v0.8.5. Canonical trainer `SKILL.md` body unchanged; routing and coaching stance unchanged.

### Changed

- **Bundled `specialists/superset/`** at v0.8.5. The status-check and job-closeout iron law now requires each touched repo's `CHANGELOG.md`, `README.md`, and roadmap doc(s) to stay aligned with shipped-vs-planned state in the same turn as the coordination SSOT update. Workers propose changelog and roadmap deltas in the daily log; the orchestrator publishes product docs on status refresh or closeout. Template: `specialists/superset/templates/status-check-changelog.md`.
- **`scripts/bundle_specialists.sh` and `scripts/verify_bundle_sync.sh`** exclude `localonly/` from bundle sync so operator workspace artifacts do not ship in the distribution bundle.
- **`README.md`** superset table row documents status-check and closeout doc hygiene alongside parallel dispatch.

### Why PATCH not MINOR

- No canonical trainer `SKILL.md` body change. The closeout rule lives in the bundled `superset` specialist, not in trainer routing prose.
- Specialist count unchanged (still 9). Bundle refresh only.

### Files touched

- `~/Projects/trainer.skill/README.md` (superset table row)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh` (`localonly` exclude)
- `~/Projects/trainer.skill/scripts/verify_bundle_sync.sh` (`localonly` exclude)
- `~/Projects/trainer.skill/specialists/superset/` (v0.8.5 bundle; commit `da7601c` and refresh)

## [0.10.1] (2026-05-20): Authoring-discipline README section + Claude-mirror resync + v0.10.0 sync-completion

**PATCH per SemVer rules.** README gains an "Authoring discipline" section that documents the three voice gates contributors apply before commit (em-dash zero, deai gate, wei-voice iron rules). The canonical SKILL.md gains no body changes; v0.10.0 (commit `ab5014b`) shipped the new § Adversarial-review pass sub-subsection but left canonical frontmatter at v0.9.1 and did not resync the Claude mirror (which still carried the pre-v0.9.1 line 269 wording). v0.10.1 finishes both syncs and ships the README authoring-discipline section in the same commit.

### Sync-completion context (v0.10.0 → v0.10.1)

L3 codification commit `ab5014b` (v0.10.0) shipped the new SKILL.md sub-subsection body and the Cursor and Windsurf trigger version stamps. It did not bump canonical SKILL.md frontmatter (remained at v0.9.1) and did not resync the Claude mirror (still carried the older paraphrasing-prone line 269 wording from before the v0.9.1 wei-voice rewrite in commit `5198365`). `verify_trainer_sync.sh` invariant 1 was FAILing on canonical-vs-Claude-mirror divergence as a result. v0.10.1 closes both gaps and stamps all four sync targets at v0.10.1.

### Added

- **`README.md` "Authoring discipline" section** (about 15 lines, between "Sync targets" and "SemVer rules"). Documents three voice gates: em-dash zero (mechanical, enforced by `scripts/verify_trainer_sync.sh` invariant 6); deai gate (manual, mandatory before claiming voice-verified, runs `python3 ~/Projects/deai.skill/deai-scan.py <file>` — or `~/.claude/skills/deai/` after `skill-sync`); wei-voice iron rules (manual: no theatrical mic-drops at paragraph end, no tricolon-after-colon, active voice with author as agent). References this CHANGELOG entry as the worked example.

### Changed

- **`~/.claude/skills/trainer/SKILL.md`** (Claude mirror) resynced byte-identical to canonical. Closes the canonical-vs-mirror divergence at line 269 that `verify_trainer_sync.sh` invariant 1 flagged after v0.9.1 landed and v0.10.0 did not address: canonical carried the wei-voice rewrite from commit `5198365` plus the v0.10.0 sub-subsection from commit `ab5014b`; the mirror retained the older paraphrasing-prone wording across both versions.
- **Canonical SKILL.md frontmatter** bumped from v0.9.1 (the bump skipped in v0.10.0) to v0.10.1.
- **Cursor trigger, Windsurf trigger** version stamps updated from v0.10.0 to v0.10.1 (both header and body references).

### Worked example: the line 269 rewrite as the four-flavor anti-pattern

The canonical SKILL.md § Decision-presentation template recommendation paragraph (line 269) before commit `5198365` read:

> Reasoning that does NOT duplicate the per-option bullets. **Use this block for:** continuation of the rationale, software-engineering best-practice context, specific research citation, deeper why-this-and-not-that comparison, or anything that addresses the operator's decision criteria rather than the options' surface properties. The recommendation reasoning is where Cascade earns its keep; the per-option bullets are table stakes.

Four iron-rule violations stacked in that single paragraph:

1. **Tricolon-after-colon.** "Use this block for:" introduced five parallel noun-phrase items, the AI / influencer / punditry shape that the wei-voice iron rules explicitly ban.
2. **Parallel-item mic-drop.** Each of the five items was grammatically parallel ("continuation of X, Y context, Z citation, Q comparison, or anything that..."), reinforcing the rhetorical-zinger effect rather than reading as integrated prose.
3. **Agent-effacing framing.** "Use this block for:" directed the reader at the block without naming Cascade as the agent doing the using; the rewrite makes Cascade the subject ("The recommendation block is where Cascade addresses...").
4. **Paraphrase-trap.** The colon-list delegated meaning to the listed items rather than asserting the recommendation block's purpose up front; readers had to read the full list before knowing what the block was for.

The rewrite (now in canonical and, with v0.10.1, in the Claude mirror) replaces the colon-list with continuous prose, names Cascade as the agent, and front-loads the recommendation block's purpose. The paragraph-end "where Cascade earns its keep; the per-option bullets are table stakes" line is preserved as the earned climactic beat of the four-paragraph subsection, not as a theatrical paragraph-end mic-drop.

### Why PATCH not MINOR

- No canonical SKILL.md body change in v0.10.1. The v0.9.1 wei-voice rewrite that v0.10.1 propagates to the Claude mirror was already committed in `5198365`; the new sub-subsection was already committed in `ab5014b` (v0.10.0).
- README section is contributor-facing documentation, not a sync target. Adding it does not change agent behavior at session start.
- Routing decision flow unchanged. Specialist list unchanged. Coaching stance unchanged.

### Files touched

- `~/Projects/trainer.skill/README.md` (new "Authoring discipline" section)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/SKILL.md` (version stamp only; line 6 frontmatter bump 0.9.1 to 0.10.1)
- `~/.claude/skills/trainer/SKILL.md` (Claude mirror; resynced byte-identical via `cp` from canonical)
- `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger; v0.10.0 to v0.10.1, header and body)
- `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger; v0.10.0 to v0.10.1, header and body)

### Why this shipped

`verify_trainer_sync.sh` invariant 1 was FAILing after v0.10.0 landed because the L3 codification commit did not complete the canonical frontmatter bump or the Claude mirror resync. README authoring-discipline section was drafted concurrently to codify the three voice gates that catch this class of regression at author time. v0.10.1 closes both gaps and ships the README section in the same commit.

## [0.10.0] (2026-05-20): Adversarial-review pass sub-subsection under Mechanical pre-action gate

**MINOR per SemVer rules** (new section added without changing existing semantics). Codifies the L3 verdict from the buds meta cycle (`buds/localonly/orchestration/2026-05-20-meta-proposals.md` § L3), ratified by Wei 2026-05-20 12:43 ET. Composes with the existing v0.6 Iron-Law mechanical pre-action gate: the 3-facts gate is the sign, the new sub-subsection is the discipline that runs when the action's reversibility cost exceeds the 3-facts gate's coverage.

### Added

- **§ Mechanical pre-action gate → Adversarial-review pass sub-subsection** (`####` nested under `### Mechanical pre-action gate`). Defines the three-step protocol: (1) enumerate N potential holes in the planned action, (2) verify each empirically with a single tool call, (3) release the gate only when all N are cleared. Trigger set is mechanically enumerated (no judgment threshold): push to origin, force-push, branch delete, PR open, merge, release tag, cross-project write. Stakes-tier override restricts the N-hole pass to vibe-careful and vibe-dangerous; vibe-safe reversible actions still take the 3-facts gate alone. Worked example references the 2026-05-19/20 buds session (14 holes total caught pre-action: 10 in initial cleanup-plan review + 4 in B1/B2 path-catchup gate; 0 surfaced post-action).

### Changed

- **Canonical, Claude mirror, Cursor trigger, Windsurf trigger** version stamps updated to v0.10.0.
- **`scripts/verify_trainer_sync.sh` Invariant 5 soft line-cap** bumped 320 → 360 to accommodate the new sub-subsection.

## [0.9.1] (2026-05-20): Decision-presentation template, anti-patterns + self-check + tightened low-stakes scope

**PATCH per SemVer rules.** Wording-only additions to the v0.9.0 Decision-presentation template subsection. No new behavior beyond what v0.9.0 already added; no routing change. Closes the failure mode where a Cascade session ships formally-compliant decision blocks that pass structural review while delivering zero decision support to the operator.

### Added

- **Anti-patterns list** under the format block. The template explicitly refuses four shapes:
  - Bullets that name a dimension without filling it.
  - Recommendation that paraphrases the per-option bullets.
  - "Both have tradeoffs" framing in the context paragraph.
  - Low-stakes label applied to decisions whose downstream consequences are unsurfaced.
- **"Inherits from Communication discipline rules above"** paragraph cross-referencing the parent Jargon / Interiority / Verbosity rules. An agent reading just the subsection still picks up parent-rule teeth (Interiority's "what you didn't weigh hard enough" is the recommendation-block expectation).
- **Self-check sentence** that Cascade applies to its own draft before posting: "Could the operator decide reading only this block, without scrolling to related artifacts or asking a follow-up?" Converts formal compliance into substantive compliance.

### Changed

- **Tightened low-stakes scope definition.** v0.9.0 defined "low-stakes" only as "operator could resolve in under thirty seconds" (an agent's subjective time estimate). v0.9.1 adds three content gates: reversible, single domain affected, no interaction with active rules or in-flight work. All four conditions must hold; if any one is uncertain, the full template applies.
- **Canonical, Claude mirror, Cursor trigger, Windsurf trigger** version stamps updated to v0.9.1.

### Why PATCH not MINOR

- Wording-only clarification under an existing subsection; no new subsection added.
- No routing decision flow change; no new behavior the trainer enforces at session start beyond what v0.9.0 already added.
- v0.9.0 added the subsection (MINOR); v0.9.1 tightens its quality bar without adding structure (PATCH).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (canonical; subsection extended + version bump)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/.claude/skills/trainer/SKILL.md` (Claude mirror; resynced byte-identical)
- `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger; version stamp)
- `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger; version stamp)

### Why this shipped

Wei's same-session followup directive after v0.9.0 landed: "ensure the decision template is not superficial." Adversarial review surfaced five superficiality risks; v0.9.1 closes four (anti-patterns, parent cross-reference, self-check, tightened scope). Risk 5 (worked-example pair) deferred to v0.9.2 if empirically needed; in the meantime the slip-past output drafted in the review session illustrates the bad-pattern anchor.

## [0.9.0] (2026-05-20): Decision-presentation template under Communication discipline

**MINOR per SemVer rules.** Communication discipline gains a new subsection (Decision-presentation template) plus a one-sentence cross-reference from the existing "Decisions, surfaced visibly" bullet. The new subsection codifies the format Cascade uses when surfacing multi-option decisions. The shape is a bolded question with two or three sentences of context, per-option bullets covering whichever grounding dimensions apply (reasons, rationale, roadmap impact, interactions, example), and a bolded recommendation whose reasoning does not duplicate the per-option bullets.

### Added

- **`### Decision-presentation template` subsection** under "Communication discipline" in canonical SKILL.md. Sits after the bulleted discipline list, before "What the trainer is NOT". Includes an explicit scope clause naming what the template covers (in-conversation multi-option surfacing) and what it does not (proposal artifacts, session logs, status updates, sub-thirty-second confirmations). The per-option bullet list is explicitly marked "use whichever apply" so single-stream decisions are not forced to manufacture cross-stream interaction notes.
- **Cross-reference from the line-235 "Decisions, surfaced visibly" bullet** to the new subsection. Existing bullet text preserved; one sentence added pointing readers at the template format.

### Changed

- **Canonical, Claude mirror, Cursor trigger, Windsurf trigger** version stamps updated to v0.9.0.
- **Soft line cap in `scripts/verify_trainer_sync.sh`** bumped from 280 to 320 to accommodate the new subsection (approximately 35 lines added).

### Why MINOR not PATCH

- Adds new behavior (a load-bearing artifact-shape rule that Cascade applies at decision-surfacing moments).
- Adds a new subsection that the existing "Decisions, surfaced visibly" bullet now cross-references rather than wholly contains.
- PATCH is reserved for renames, typos, sync-mechanic improvements, and wording-only clarifications. The v0.8.0 dispatch-graph sub-clause is the matching precedent for the MINOR call: it also added a sub-clause under existing structure and introduced new operational behavior without changing routing.

### Why MINOR not MAJOR

- Routing decision flow unchanged.
- Specialist gym-skills list unchanged (still 9).
- Teaching-responsibility tiers unchanged.
- Coaching stance, Iron Laws, Red Flags, and Rationalizations table all byte-identical to v0.8.0.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (canonical; new subsection, line-235 cross-reference, version bump)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (soft line cap bump)
- `~/.claude/skills/trainer/SKILL.md` (Claude mirror; resynced byte-identical via skill-sync)
- `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger; version stamp via skill-sync)
- `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger; version stamp via skill-sync)

### Companion operator-domain steps shipped alongside this version

- Delete `MEMORY[1adcc98e]` ("Inline questions with rationale"). The new SKILL.md subsection structurally supersedes the memory; keeping both creates duplicate discipline that eventually disagrees. Operator runs the deletion via Cascade memory tooling at ratification.
- Run `skill-sync` after canonical edit to propagate to the three mirrors.
- Run `~/Projects/trainer.skill/scripts/bundle_specialists.sh` per the standing discipline of refreshing the bundle after every trainer canonical edit (this version does not affect bundled specialists, but the discipline of running the bundle script remains the safe default).
- Run `bash ~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` to confirm all invariants pass post-edit.

## [0.8.0] (2026-05-19): Dispatch-graph-before-dispatch iron-law sub-clause

**MINOR per SemVer rules.** Adds a new sub-clause under the "Iron Law: plan first, implement second" section: the plan-first discipline extends to the dispatch graph itself. Before any multi-agent batch is generated, a daily-log manifest must exist at `<project>/localonly/daily/<YYYY-MM-DD>.md`, validated by `superset`, with all dependency edges surfaced to the user. Cascade auto-drafts the manifest on dispatch-intent triggers; runs a self-adversarial review pass using superset's falsifier checklist plus a form-check adversarial-review against its own draft; surfaces validated manifest plus findings before generating per-agent prompts.

### Added

- **`### Dispatch graph before dispatch` sub-clause** under "Iron Law: plan first, implement second" in canonical SKILL.md. Names the trigger phrases that violate the iron law ("just dispatch them, I'll review later"; "skip the manifest this time"; etc.). Names the two anchor incidents: mailchimp 2026-05-18 duplicate dispatch (Agent B); buds 2026-05-19 f-droid research and LICENSE edit dispatched in parallel without a producer-consumer link. Also names the three-layer agent architecture (orch 1-day, meta 1-week, worker per-task) at a brief level; routes to `superset.skill` for operational detail.

### Changed

- **Soft line cap in `scripts/verify_trainer_sync.sh`** bumped from 240 to 280 to accommodate the new sub-clause (~22 lines added).
- **Canonical, Claude mirror, Cursor trigger, Windsurf trigger** version stamps updated to v0.8.0.
- **New invariant 9 in `scripts/verify_trainer_sync.sh`** (script-tooling-only change, no SKILL.md content change, no version bump). Runs the superset falsifier harness at `$HOME/Projects/superset.skill/scripts/falsifier-harness/run-all.sh` and FAILs the verify pass if the harness exits non-zero. Falls back to WARN + skip if the harness script is not present (trainer can theoretically release without superset bundled, though current bundle ships it). errexit suspension around the harness invocation so a harness failure produces full diagnostic output (the failing test name plus the validator's stderr JSON) rather than silently exiting. Tested both positive (clean baseline: 6 hypotheses verified, exit 0) and negative (corrupted valid-baseline fixture: invariant 9 FAILS with full diagnostic including which test failed and which falsifier the validator raised). The harness regression is now part of every bundle-refresh verify gate.

### Why MINOR not PATCH

- Adds new behavior (auto-invoke + self-adversarial review on dispatch triggers).
- Adds a new iron-law sub-clause that route-corrects on specific user phrases.
- PATCH would be wording-only; this introduces a new rule.

### Why MINOR not MAJOR

- Routing decision flow unchanged.
- Specialist gym-skills list unchanged (still 9).
- Teaching-responsibility tiers unchanged.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (canonical; new sub-clause + version bump)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (line-cap bump)
- `~/.claude/skills/trainer/SKILL.md` (Claude mirror; resynced byte-identical)
- `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger; version stamp)
- `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger; version stamp)

### Downstream changes shipped alongside this version

- `superset.skill` v0.4.0 (sibling release): adds daily-log-driven dispatch section, promotes M6/M11/M12 to High, adds H14 (artifact-existence) and H15 (daily-log-precondition) falsifiers, ships new `templates/daily-log.md` and `templates/high-stakes-list.yaml`. See `superset.skill/CHANGELOG.md` v0.4.0 entry.

## [0.7.1] (2026-05-18): Rename 9th specialist `ancillary` → `superset` for gym-family coherence

**PATCH per SemVer rules.** The 9th specialist added in v0.7.0 under the name `ancillary` is renamed to `superset` so its label fits the gym-themed naming convention shared with the other eight specialists (`form-check`, `program`, `warmup`, `safetybar`, `recovery`, `gymbuddy`, `diet`, `pr`). The routing flow, coaching stance, Iron Laws, and the specialist's behavior are byte-equivalent to v0.7.0; only the surface name changed.

### Changed

- **Canonical sibling directory:** `~/Projects/ancillary.skill/` → `~/Projects/superset.skill/` (full rename with internal references updated; old name preserved in CHANGELOG history of that repo and in the routing-table parenthetical of the canonical trainer SKILL.md).
- **Bundle directory:** `specialists/ancillary/` → `specialists/superset/`. All twelve bundled files inside reflect the new name.
- **`composes:` frontmatter entry:** `ancillary` → `superset` (9 entries unchanged in count).
- **`description` frontmatter:** routing list reads `... / pr / program / warmup / superset` (rename only).
- **SKILL.md specialist table row:** the 9th row's name reads `superset` with a parenthetical `(formerly ancillary through v0.7.0)` to preserve the historical pointer.
- **SKILL.md "Bundled specialists" section:** mentions the v0.7.1 rename with a one-line history note.
- **README.md:** every current-state mention of `ancillary` updated to `superset`; the repo-layout diagram's 9th row notes the rename history.
- **`scripts/bundle_specialists.sh` SPECIALISTS array:** `ancillary` → `superset`.
- **`scripts/verify_bundle_sync.sh` SPECIALISTS array:** `ancillary` → `superset`.
- **Cursor + Windsurf trigger files:** `~/Projects/.cursor/rules/trainer.mdc` and `~/Projects/.windsurf/rules/trainer.md` version stamps and quick-reference lists updated.
- **Claude mirror:** `~/.claude/skills/trainer/SKILL.md` resynced from canonical.

### Why this version is PATCH not MINOR

- The specialist list count is unchanged (still 9). No routing decisions change, no new sync target is added, no specialist's invocation pattern is updated.
- The rename is a surface-label clarification driven by family coherence with the other gym-themed specialist names. Existing agents that route to `ancillary` should be updated; the rename is documented in the v0.7.0 entry below and in the routing-table parenthetical so consumers can find the new name.
- One MAJOR-flavored concern is that downstream agents with hard-coded references to `ancillary` will break. The mitigation is the parenthetical pointer in the routing table and a `(formerly ancillary)` note in the canonical SKILL.md; a hard alias is not maintained because the rename happened in a single same-day patch window with no other consumers.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (version, composes, description, routing-table row, bundled-specialists note)
- `~/Projects/trainer.skill/README.md` (current-state prose, table row, repo-layout)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh`
- `~/Projects/trainer.skill/scripts/verify_bundle_sync.sh`
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (soft cap bumped to accommodate the new routing-table parenthetical)
- `~/Projects/trainer.skill/specialists/ancillary/` → `~/Projects/trainer.skill/specialists/superset/` (12 files, full bundle refresh from the renamed canonical sibling)
- `~/Projects/superset.skill/` (canonical sibling; rename of `~/Projects/ancillary.skill/`)
- `~/.claude/skills/trainer/SKILL.md` (resynced from canonical)
- `~/Projects/.cursor/rules/trainer.mdc` (version stamp + quick-reference list)
- `~/Projects/.windsurf/rules/trainer.md` (version stamp + quick-reference list)

## [0.7.0] (2026-05-18): Add `ancillary` as 9th specialist (parallel-agent dispatch discipline)

**MINOR per SemVer rules; see "Why this version is MINOR not MAJOR" below.** The trainer's specialist gym-skills list grows from 8 to 9 with the addition of `ancillary`, a parallel-agent dispatch and isolation discipline. Routing flow, coaching stance, and Iron Laws are unchanged for the existing 8 specialists; `ancillary` is additive.

### Added

- **`ancillary` as the 9th specialist** at `specialists/ancillary/` (12 files: SKILL.md, README, CHANGELOG, ROADMAP, LICENSE, agent-prompt template, batch-aggregation template, orchestrator-handoff-prompt template, session-log template, falsifier-checklist reference, role-overlays reference, runtime-portability reference). Borrowed patterns from `obra/superpowers-skills` (worktree discipline), `Ibrahim-3d/orchestrator-supaconductor` (role-archetype framing), and `usemozzie/mozzie` (file-ownership table). The canonical sibling repo at `~/Projects/ancillary.skill/` is the editing home; the bundle copy refreshes via `scripts/bundle_specialists.sh`.
- **Routing entry for parallel-agent dispatch.** SKILL.md routing flow step 1 gains "Spawning 2+ parallel agents on the same repo → `ancillary`." Step 2 gains "Parallel-agent dispatch at any tier → load `ancillary` for worktree-isolation and prompt-template discipline." Step 3 gains an example of mid-session route to `ancillary` for orchestrator-handoff under context-window pressure.
- **`composes:` frontmatter entry** for `ancillary` (now 9 entries).
- **`description` frontmatter expansion.** Triggers list adds "parallel agent dispatch" and "orchestrator handoff" so the description discoverability covers `ancillary`'s use cases.
- **`bundle_specialists.sh` SPECIALISTS array** gains `ancillary`. Comment updated from "8 specialist gym-skills" to "9 specialist gym-skills."
- **`README.md` table** for the 9 specialists, with `ancillary`'s row pointing at the dispatch / isolation / orchestrator-handoff role.
- **`README.md` repo-layout diagram** lists `specialists/ancillary/` with a v0.7.0 marker.

### Changed

- **SKILL.md heading** "The 8 specialist gym-skills" → "The 9 specialist gym-skills."
- **"Bundled specialists" section** in SKILL.md notes the v0.7.0 specialist count.
- **`scripts/verify_trainer_sync.sh` soft cap bumped from 180 to 240 lines.** The canonical SKILL.md is 228 lines after the v0.7.0 ancillary additions plus the accumulated v0.6.x Iron Law mechanical pre-action gate and its worked examples. The 180 cap fired a WARN on every verify; new cap leaves room for the next routine specialist addition without immediately tripping the warning.
- **`scripts/verify_bundle_sync.sh` SPECIALISTS array** gains `ancillary` so bundle-drift detection covers all nine specialists.

### Why this version is MINOR not MAJOR

- The SemVer rule "specialist gym-skills list gains or loses entries" was authored with breaking changes in mind (renames, removals, semantic shifts in routing for existing entries). Pure additions to the list are additive per pre-1.0 convention: existing agents that route to the 8 v0.6.1 specialists continue to route exactly the same way, with no changes to their routing decisions.
- The v0.3.0 precedent ("Why this version is MINOR not MAJOR") established that purely additive changes to the bundle are MINOR. The same logic applies here: `ancillary` is opt-in for the parallel-agent dispatch trigger, not in the path of any existing specialist's routing.
- The routing decision flow's text gains three sentences (one per step) about `ancillary`, with zero modification to the existing routing text.
- Coaching stance, Iron Laws (plan-first + mechanical pre-action gate), Red Flags, and Rationalizations tables are all byte-identical to v0.6.1.

### Hard-rule compliance

- Zero em-dashes across the new `ancillary` files, the trainer SKILL.md edits, the README edits, and this CHANGELOG entry.
- The `bundle_specialists.sh` change is a one-line array extension; the existing rsync invariants are preserved.
- Voice rules apply to `ancillary`'s README, CHANGELOG, ROADMAP, and SKILL.md prose: active voice, no "X, not Y" comma-joined patterns, no tricolon-after-colon, no theatrical paragraph-end mic-drops.

### Borrowings cited (transitive, via `specialists/ancillary/CHANGELOG.md`)

`ancillary` v0.2.0 borrows specific patterns from three public projects, documented inline in its CHANGELOG and README. The trainer's repository inherits these citations transitively via the bundle:

- `obra/superpowers-skills` (660 stars, archived) for worktree-directory-selection priority, gitignore pre-flight, project-setup auto-detect, and clean-baseline verification.
- `Ibrahim-3d/orchestrator-supaconductor` (350 stars) for the role-archetype framing.
- `usemozzie/mozzie` (49 stars) for the file-ownership table pattern.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (version bump 0.6.1 → 0.7.0; composes field; description; routing flow; specialist table; "Bundled specialists" section)
- `~/Projects/trainer.skill/README.md` (8 → 9 references; new ancillary row in table; repo-layout diagram)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh` (SPECIALISTS array; comment)
- `~/Projects/trainer.skill/specialists/ancillary/` (new directory, 12 files)
- `~/Projects/ancillary.skill/` (new sibling canonical, 13 files including `.gitignore`)
- `~/.claude/skills/ancillary.skill/` (renamed from `~/.claude/skills/ancillary/`; mirrored from canonical)

### Open questions

- **Specialist-list SemVer rule.** The current rule ("specialist list gains or loses entries → MAJOR") needs refinement to distinguish additive vs breaking changes. Consider updating to "specialist list gains or loses entries breaks existing routing → MAJOR; purely additive → MINOR" in a future patch.
- **Cursor / Windsurf rule mirrors.** The trainer SKILL.md is mirrored to `~/Projects/.cursor/rules/trainer.mdc` and `~/Projects/.windsurf/rules/trainer.md`. The v0.7.0 SKILL.md changes need to flow to those mirrors; run `skill-sync` after this commit.
- **Public push.** This entry is committed locally; pushing to `weijia-89/trainer.skill` should happen after `verify_trainer_sync.sh` runs clean.

---

## [0.5.0] (2026-05-16): Runnable pressure-scenario harness (3 trainer scenarios in form-check shape) + soft-cap bump

**MINOR per SemVer rules.** Routing decision flow and specialist list unchanged. The v0.4.0 doc-only pressure scenarios at `tests/scenarios/S01_*.md`, `S02_*.md`, `S03_*.md` are now also instantiated as runnable harness scenarios under `tests/scenarios/harness/<name>/` matching the form-check pressure-scenario shape (`setup.md` + `prompt.md` + `pass_criteria.py` + `notes.md` + `reference_response.md`). Doc-only scenarios are retained as the human-readable spec.

### Added

- **`tests/scenarios/harness/_grading.py`** vendored from `form-check.skill/tests/pressure_scenarios/_grading.py` (same `Transcript` substantive-sentence helper; same min-words floor of 10 for `__contains__`).
- **`tests/scenarios/harness/ceremonial_routing/`** harness shape for S01. Reference response passes its own `pass_criteria.py`.
- **`tests/scenarios/harness/coaching_collapse_on_i_know/`** harness shape for S02. Reference response passes its own `pass_criteria.py`.
- **`tests/scenarios/harness/bypass_for_small_task/`** harness shape for S03. Reference response passes its own `pass_criteria.py`.

### Changed

- **`scripts/verify_trainer_sync.sh`** soft cap bumped from 140 to 180 lines. Canonical `SKILL.md` is now 157 lines after the v0.4.0 Red Flags + Rationalizations additions; the previous 140 cap fired a `WARN` on every verify. New cap leaves headroom for incremental discipline-floor scaffolding without immediately tripping the warning.

### Not changed

- `SKILL.md` content (no normative additions beyond v0.4.0).
- README scope (already updated in v0.4.0 to acknowledge documentation-skill vs behavioral-skill distinction).
- The 4 sync targets (canonical, Claude mirror, Cursor trigger, Windsurf trigger) all agree on version 0.5.0 after this entry; verify with `bash scripts/verify_trainer_sync.sh`.

### Verification

- `tests/scenarios/harness/<name>/pass_criteria.py` passes against its corresponding `reference_response.md` for all 3 scenarios (3/3 PASS).
- `bash scripts/verify_trainer_sync.sh` reports PASS on all 7 invariants (version agreement, em-dash zero, trigger config, byte-identical mirror).
- `form-check.skill/tests/pressure_scenarios/discriminate_test.py` (mutation-style probe) still reports 0/272 incorrect passes after Option C upgrade of all 34 form-check pass_criteria.

### Known follow-ups

- **Phase 11 blind audit cycle** still pending. Requires `ANTHROPIC_API_KEY` or alternate-vendor harness; not autonomously runnable.
- **Layer B (calibration log analyzer) and Layer C (mutation testing of agent behavior)** of the Phase 11 plan remain future work; v0.5.0 is Layer A only (per-scenario pass/fail harness).

## [0.4.0] (2026-05-16): Load-bearing-discipline pass (audit-gap patches + Iron Law + Red Flags + Rationalizations + pressure scenarios)

**MINOR per SemVer rules.** Routing decision flow and specialist list unchanged; coaching-stance section gains explicit operational definitions and the discipline-floor scaffolding (Iron Law, Red Flags, Rationalizations) that the other 7 gym-skills already had.

Two converging inputs drove this version:

1. **A targeted audit of the v0.3.0 trainer skill** identified 4 operationalization gaps + 1 schema gap (Iron Law, demonstrated-understanding, adversarial-review interaction, opt-out semantics, override-log schema). The audit document itself is private working notes; the gaps it surfaced are described inline below.
2. **Context-free adversarial review at v0.3.0** (chat 2026-05-16, late) added 4 more items (Red Flags section, Rationalizations table, calibration log infrastructure, README walk-back of v0.3.0 promotional phrasing), plus three doc-only pressure scenarios for the failure modes.

The v0.3.0 portfolio-bundling work made the skill *distributable*; v0.4.0 makes the skill's stated discipline more *enforceable* by surfacing the failure modes the discipline is supposed to prevent.

### Added (SKILL.md)

- **Iron Law banner** at the top of the Coaching stance section. Form: *"coach, do not do. Push back when warranted. Defer when the user has demonstrated understanding. Log coached overrides."* Trainer was the only gym-skill without one as of v0.3.0; closes audit Gap 1.
- **Coached-override log entry schema inline.** Schema: `{ts, event, subject, trainer_position, user_decision, user_rationale, residual_concern, rounds}`. Closes audit Gap 5 (override log was prescribed in v0.2.0 but schema-undefined).
- **Red Flags section.** 10 verbatim agent-thoughts that should trigger STOP and re-route (e.g. "I named the specialist; that counts as invoking it", "User said 'I know'; I'll defer"). Matches form-check's structural pattern; sourced from the dominant failure modes in the adversarial review.
- **Rationalizations table.** 8 excuse / reality pairs covering ceremonial routing, coaching collapse, framing-based bypass, hidden-state coaching.
- **Adversarial-review deference** added to "What the trainer is NOT". During `form-check adversarial-review`, the trainer steps back on review content but stays engaged on routing decisions (which specialist next, when to stop). Closes audit Gap 3.
- **Opt-out semantics** as a new section. Per-session opt-out via "no coaching this session"; routing questions still answered, pushback paused. Persistent opt-outs are themselves a signal logged at the start of the next non-opted-out session. Closes audit Gap 4.

### Added (filesystem)

- **`form-check.skill/.recovery/calibration.jsonl`** (empty, append-only). Backs the pointer in `SKILL.md` which was previously dangling (verified by `ls` before the fix: directory did not exist).
- **`form-check.skill/.recovery/SCHEMA.md`** documenting event types: `coached_override`, `coaching_collapse`, `routing_decision`, `score_event`, `coached_override_revisit`. Append-only, UTC timestamps, no-PII discipline stated.
- **Three doc-only pressure scenarios** under `trainer.skill/tests/scenarios/`:
  - `S01_ceremonial_routing.md`, tests Iron Law + Red Flag "I named the specialist; that counts as invoking it"
  - `S02_coaching_collapse_on_i_know.md`, tests the tightened defer-clause against vague approval
  - `S03_bypass_for_small_task.md`, tests the always-on claim against user-framed-small tasks that hide tier-relevant context
  - Each follows the Phase 11 plan schema (Setup, Forcing function, Pass criteria, Fail criteria, Trapdoor). Manually testable by a human; runnable harness deferred to Phase 11 implementation.
- **`tests/scenarios/README.md`** documenting the manual test protocol and pass/fail mapping back to `SKILL.md` clauses.

### Changed

- **"Demonstrated understanding" clause tightened.** Previously: *"User has demonstrated understanding of the tradeoff and has a reasoned position."* Now: *"User has articulated the specific consequence the trainer named AND the specific reason it does not apply or is acceptable. Vague approval ('yes I know', 'I've got this', 'trust me') does not count as demonstrated understanding."* Closes audit Gap 2 (was the most exploitable clause in v0.3.0).
- **`README.md` honest-scope paragraph added.** Walks back v0.3.0 promotional phrasing ("8-skill agent ecosystem", "makes the ecosystem coherent"). New framing: documentation skill with discipline scaffolding, not yet a behavioral skill with a runnable harness. References the audit and the Phase 11 plan.
- **`README.md` repo-layout diagram** updated to include `tests/scenarios/`.
- **Soft line cap** bumped from 100 to 140 in `scripts/verify_trainer_sync.sh`. Canonical `SKILL.md` is now 157 lines. The cap will need another tune-up at next discipline-pass; see open items.

### Why MINOR not MAJOR

- 8 specialists unchanged.
- Routing decision flow byte-identical.
- Push-back triggers unchanged in category (still 3 triggers: concrete consequence, best-practice deviation, missing skill).
- New operational definitions and discipline scaffolding are clarifications + enforcement aids, not new behaviors. Any v0.3.0-compliant trainer is already v0.4.0-compliant; the v0.4.0 version is harder to game.

### Verification done

- `ls $HOME/Projects/form-check.skill/.recovery/` returns `calibration.jsonl` + `SCHEMA.md`.
- Em-dash audit: zero across `SKILL.md`, all three mirrors, this CHANGELOG entry, `SCHEMA.md`, the three scenarios, `README.md`, and `scripts/bundle_specialists.sh`.
- Bundle script re-run confirms 280 files across 8 specialists at `./specialists/`.
- `verify_trainer_sync.sh` invariants pass (canonical, Claude mirror, Cursor and Windsurf triggers all agree on version 0.4.0; zero em-dashes; `alwaysApply: true`; `trigger: always_on`).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (Iron Law, log-schema-inline, Red Flags, Rationalizations, defer tightening, adversarial-review carve-out, opt-out semantics; 103 → 157 lines)
- `~/.claude/skills/trainer/SKILL.md` (byte-identical mirror, re-synced to v0.4.0 on second pass; first pass missed the Red Flags + Rationalizations block, caught by `verify_trainer_sync.sh`)
- `~/Projects/.cursor/rules/trainer.mdc` (heading bumped to v0.4)
- `~/Projects/.windsurf/rules/trainer.md` (same)
- `~/Projects/trainer.skill/README.md` (honest-scope paragraph, layout diagram updated)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (line cap 100 → 140)
- `~/Projects/trainer.skill/tests/scenarios/` (new dir, 4 files)
- `~/Projects/form-check.skill/.recovery/calibration.jsonl` (new, empty)
- `~/Projects/form-check.skill/.recovery/SCHEMA.md` (new)
- a private trainer-skill audit (working notes) (source audit doc; not in the skill repo)

### Open items deferred to next version

- **Phase 11 runnable harness** for the three pressure scenarios: doc-only at v0.4.0. The scenarios are testable manually; no automation submits them to an agent and scores behavior. Estimated 4-8 hr; deferred until external pressure (interview, public release, third party using the skill) makes the runnable case load-bearing.
- **`SKILL.md` line count at 157 already pushes the 140 cap** added in this version. Next discipline-pass should either re-tune the cap or split Red Flags + Rationalizations into a separate `discipline.md` companion. Splitting trades token efficiency (some agents skip companions) for the cap.
- ~~**Re-run `verify_trainer_sync.sh`**~~ Done. All 7 hard invariants PASS; the only WARN is the documented `SKILL.md` line count (157) over the bumped soft cap (140), tracked above.

---

## [0.3.0] (2026-05-16): Bundle the 8 specialists into the repo; rewrite README for portfolio distribution

**MINOR per SemVer rules.** Routing flow and coaching stance unchanged; new packaging mechanic added so the repo distributes the full 8-skill ecosystem rather than only the trainer entrypoint.

### Added

- **`specialists/` directory** with all 8 specialist gym-skills bundled in. Contents:
  - `specialists/form-check/` (243 files: SKILL.md, README, CHANGELOG, agent-runtime, checklists, docs, examples, learner, multi-language, references, rubrics, scale-up, templates, tests, tools)
  - `specialists/recovery/` (18 files: checklists, examples, references, rubrics, templates, tests, workflow)
  - `specialists/warmup/` (4 files, includes `graduation_checklist.md`)
  - `specialists/gymbuddy/`, `specialists/safetybar/`, `specialists/diet/`, `specialists/pr/`, `specialists/program/` (3 files each: SKILL.md, README, CHANGELOG)
  - Total bundled: 280 files across 8 specialists.
- **`scripts/bundle_specialists.sh`** refreshes the bundle from sibling-dir canonicals. Excludes `.git`, virtualenvs, `__pycache__`, `node_modules`, `.DS_Store`, `.pytest_cache`, `.recovery` state, generated test output. Idempotent via `rsync --delete`.
- **`composes:` frontmatter populated** in `SKILL.md` with the 8 specialist names.
- **"Bundled specialists" section in `SKILL.md`** explaining the relationship between sibling-dir canonicals (editing home) and bundle (distribution artifact).

### Changed

- **`README.md` rewritten** as public-portfolio-facing document. Was internal-skill-doc style; now opens with the "8-skill agent ecosystem" framing, includes install/use snippets, repository-layout diagram, and explicit separation between SKILL.md sync (canonical-to-mirrors, four locations) and bundle (canonical-to-`./specialists/`, one operation).
- **`SKILL.md` references** to specialist paths kept as `<name>.skill/` (sibling convention) in routing/teaching sections because the canonical operating environment is the home directory with sibling skill dirs; the bundle is for clones / distribution, not for local editing.
- **SemVer rules updated** to clarify that introducing the bundle mechanic is a MINOR change.

### Why this version is MINOR not MAJOR

- The 8 specialists in the `composes:` list are the same 8 specialists already documented in v0.2.0's body. No specialist added or removed.
- Routing decision flow is byte-identical to v0.2.0.
- Coaching stance criteria unchanged.
- The bundle is additive: agents that operate against sibling-dir canonicals continue to work unchanged.

### Hard-rule compliance

- Zero em-dashes across `SKILL.md`, `README.md`, this CHANGELOG entry, and the new bundle script.
- Bundle script uses single-quoted exclude patterns (no shell-glob surprises) and `set -euo pipefail` for fail-fast.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (version bump 0.2.0 → 0.3.0; composes field populated; bundled-specialists section added)
- `~/Projects/trainer.skill/README.md` (rewrite, 60 → ~135 lines)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh` (new)
- `~/Projects/trainer.skill/specialists/` (new directory, 280 files across 8 specialists)

### Open questions

- **Mirror updates:** the `~/.claude/skills/trainer/SKILL.md` mirror needs a re-sync to pick up the v0.3.0 composes field and the new section. Run `scripts/verify_trainer_sync.sh` after mirror update.
- **Sync of bundled specialists:** the bundle currently lives only inside `trainer.skill`. If `~/.claude/skills/trainer/` should also carry the bundle (so Claude can read specialists without leaving its skill dir), that's a separate sync step worth deciding on before pushing public.
- **Public push:** repo is not yet pushed to GitHub. When ready, decide on repo visibility (public for portfolio vs private), tags / release for v0.3.0, and whether `LICENSE` and `CONTRIBUTING.md` need adding at the top level (currently only inside specialists like `form-check`).

---

## [0.2.0] (2026-05-16): Coaching stance correction; always-on triggers

**Breaking-semantic change.** v0.1.0 said "user wishes are the final say." Wei corrected this: the trainer is a coach, not a doormat. The trainer should push back when user decisions have deleterious downstream consequences or veer from best practices without articulated reason. After two rounds of coached pushback, the trainer respects the decision and logs it as a *coached override* with the user's rationale.

### Changed

- **Coaching stance section added.** Three push-back triggers (concrete downstream consequence; veers from best practice without articulated reason; user missing a skill that would change the decision). Procedure: name consequence, cite practice, offer alternative; two rounds max; log coached override.
- **Proactive teaching responsibilities expanded.** Trainer now explicitly explains: specialist composition (which order, why, how they interact), downstream consequences (what to watch for after a change), best practices (cited from `form-check.skill/references/notes.md` at the moment of relevance).
- **Triggers changed to always-on.** Cursor trigger: `alwaysApply: true`. Windsurf trigger: `trigger: always_on`. Loaded first on every coding / prompt-engineering / agent-skill session.
- **Removed "user wishes are the final say"** language entirely. Replaced with the coaching-with-audit-trail model.
- **README.md added** documenting all four sync targets and SemVer rules. The Phase 10 routing decision (whether to fold trainer into `warmup` or stand it up separately) was driven by a private gym-skills evidence audit; the decision and rationale are summarized in `docs/PHASE_10_ROUTING_DECISION.md` when that doc exists.

### Hard-rule compliance

- Zero em-dashes in `SKILL.md`, both triggers, README, and this CHANGELOG entry (matches Wei's writing-style hard rule from 2026-05-15).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (rewrite; 88 lines)
- `~/.claude/skills/trainer/SKILL.md` (byte-identical mirror)
- `~/Projects/.cursor/rules/trainer.mdc` (always-apply, updated body)
- `~/Projects/.windsurf/rules/trainer.md` (always-on, updated body)
- `~/Projects/trainer.skill/README.md` (new)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (bumped expected version to 0.2.0; bumped soft line cap from 80 to 100)

### Companion: `skill-sync` gains Windsurf support

`skill-sync` v0.2+ adds Windsurf as a sync target alongside Claude and Cursor. The trainer skill is the first to use it. See `~/.claude/skills/skill-sync/CHANGELOG.md` for the implementation detail.

## [0.1.0] (2026-05-16): Initial scaffold

- Created as the bootstrap / entrypoint skill for the gym-skills family (Phase 10 of the gym-skills evidence-base audit, 2026-05-16).
- Role defined: "helps the user find the program that works for them, teaches them how to do it along the way, and adjusts according to the user's wishes." Authored by Wei Jia.
- Sync targets established at four locations:
  - `~/Projects/trainer.skill/SKILL.md` (canonical)
  - `~/.claude/skills/trainer/SKILL.md` (Claude mirror, byte-identical)
  - `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger)
  - `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger)
- `scripts/verify_trainer_sync.sh` added to assert sync invariants.
- Lists the 8 specialist gym-skills (`form-check`, `program`, `warmup`, `safetybar`, `recovery`, `gymbuddy`, `diet`, `pr`) with one-line invocation criteria.
- Names "user wishes are the final say" as the trainer's behavioral anchor: overrides are respected and noted, never argued. (Reversed in v0.2.0.)
- No checklists, no rubrics, no scoring. Pure routing + teaching + adapting.
