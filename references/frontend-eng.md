# references/frontend-eng.md — L2 frontend engagement reference

**Source:** emilkowalski/skills@de33dbe (L2 upstream)  
**Track:** B (no internal overlap → hardened-acquisition plan)  
**Lane:** L2 (trainer.skill, trivial weight)  
**Generated:** 2026-08-11 (operator-resolved L2 scope/structure/tooling/versioning decisions)  

---

## Executive summary

trainer.skill has **zero frontend coverage** — the mandate hypothesis ("covers it weakly") is REFUTED; reality is absent, not weak. emilkowalski/skills is MIT-licensed, 17 files, 100% Markdown, zero runtime/deps/hooks — trivial weight confirmed.

The L2 acquisition fills the frontend engagement gap by emitting a kickoff prompt for EVERY frontend gap found (52 total: 42 upstream behaviors + 10 uncovered domains). This reference file captures the design principles, anti-patterns, and routing rules for trainer-facing frontend guidance.

---

## 1. Core design principles (from emilkowalski/skills)

| Principle | UP-Behind | trainer.skill status |
|---|---|---|
| Should it animate? | UP-B01 | absent |
| Animation decision tree + custom curves | UP-B02 | absent |
| Easing + custom curves | UP-B03 | absent |
| Duration budgets per element | UP-B04 | absent |
| Spring animation config | UP-B05 | absent |
| Button press feedback (scale 0.97 on :active) | UP-B06 | absent |
| Never scale(0) — start from scale(0.9-0.97) | UP-B07 | absent |
| Origin-aware popovers (transform-origin at trigger) | UP-B08 | absent |
| Tooltip skip-delay on subsequent hovers | UP-B09 | absent |
| CSS transitions over keyframes for interruptible UI | UP-B10 | absent |
| Blur masking for imperfect crossfades | UP-B11 | absent |
| @starting-style for entry animations | UP-B12 | absent |
| CSS transform mastery (translate%, scale children, 3D) | UP-B13 | absent |
| clip-path animation toolkit | UP-B14 | absent |
| Gesture/drag interactions (momentum, damping, capture) | UP-B15 | absent |
| Performance rules (transform+opacity only, WAAPI) | UP-B16 | absent |
| Accessibility (reduced motion + touch hover gating) | UP-B17 | absent |
| Stagger animations (30-80ms) | UP-B18 | absent |
| Debugging animations (slow-mo, frame-by-frame) | UP-B19 | absent |
| Required review format (Before/After/Why table) | UP-B20 | absent |
| Asymmetric enter/exit timing | UP-B21 | absent |
| Fluid interface principles (response, 1:1, interruptibility) | UP-B22 | absent |
| Apple spring params (damping ratio + response) | UP-B23 | absent |
| Velocity handoff (gesture → spring) | UP-B24 | absent |
| Momentum projection (exponential-decay) | UP-B25 | absent |
| Spatial consistency (symmetric paths, anchored origins) | UP-B26 | absent |
| Rubber-banding (soft boundaries) | UP-B27 | absent |
| Gesture design details (tap, drag, parallel detection) | UP-B28 | absent |
| Materials & depth (translucency, backdrop-filter) | UP-B29 | absent |
| Multimodal feedback (motion + sound + haptics) | UP-B30 | absent |
| Accessibility — three signals (motion, transparency, contrast) | UP-B31 | absent |
| Typography (optical sizing, tracking, leading) | UP-B32 | absent |
| Apple's 8 design principles | UP-B33 | absent |
| Process (prototype interactively, test with real people) | UP-B34 | absent |
| Animation term reverse-lookup glossary (~60 terms) | UP-B35 | absent |
| Animation construction sequence (7-step build) | UP-B36 | absent |
| Never Ship checklist (13 auto-block items) | UP-B37 | absent |
| Opportunity-finding gate + hunt patterns | UP-B38 | absent |
| Animation review (10 standards, 14 triggers, 9-level hierarchy) | UP-B39 | absent |
| Codebase animation audit (recon/audit/vet/plan) | UP-B40 | absent |
| UI variant prototyping (divergence + picker) | UP-B41 | absent |
| Curated UI library picker | UP-B42 | absent |

**Key finding:** Every single one of the 42 upstream behaviors is `theirs-only` (present only upstream, absent in trainer.skill). The absence IS the gap, not a design decision.

---

## 2. Uncovered frontend domains (neither side covers)

| Domain | GAP-Nxx | Why it matters for trainer |
|---|---|---|
| RTL / bidirectional layout animation | N01 | trainer's form-check specialist has an a11y checklist; RTL animation intersects motion + accessibility |
| Responsive / adaptive animation | N02 | trainer routes to form-check for responsive review; motion-specific responsive guidance is missing |
| Typography taste beyond Apple principles | N03 | trainer has no typography guidance; apple-design covers tracking/leading only incompletely |
| Color systems and dark-mode animation | N04 | form-check has WCAG 2.2 checklist but no motion-specific color guidance |
| Data visualization animation | N05 | trainer routes to form-check for data-viz review; no motion guidance exists |
| Microcopy / UI text in motion | N06 | trainer has no content/microcopy guidance; intersects with i18n |
| Performance budgeting for motion | N07 | trainer's diet specialist covers token budgets; no motion-performance budget exists |
| Motion design tokens | N08 | trainer has no design-system guidance; architectural gap for token architecture |
| Framework-specific motion patterns | N09 | trainer is framework-agnostic; a frontend specialist should cover multiple frameworks or declare scope |
| Animation testing strategy | N10 | trainer's form-check has testing checklists; no animation-specific testing strategy exists |

**Key finding:** 10 uncovered domains where emilkowalski/skills is silent AND trainer.skill has no coverage. The mandate requires kickoff prompts for these too.

---

## 3. Routing rules for trainer.skill

**Trainer iron-law cross-consumers (non_negotiable #4):** trainer.skill's core routing must not be altered to accommodate frontend content. Any frontend additions must surface via reference files, not routing changes.

**Conventional Commits with scope:** Any add-to-trainer commit must use `scope: frontend-eng` or equivalent per trainer SemVer rules. A MINOR version bump is appropriate for additive reference-file content.

**Static-decline execution:** L2 tooling now lifts static-decline for Phase 5+ (same posture as L3). Trainer test suite can run locally during implementation.

---

## 4. Gap coverage map

**42 upstream behaviors (UP-B01 through UP-B42):** All `theirs-only`. Each is a frontend gap in trainer.skill. The L2 acquisition should address these via the reference file content + kickoff prompts.

**10 uncovered domains (GAP-N01 through GAP-N10):** Neither emilkowalski/skills nor trainer.skill covers these. These are architectural / cross-cutting gaps that the reference file documents but does not fully resolve.

**Total: 52 gaps.** Kickoff prompt emission is the L2 deliverable (see L2-GAP-PROMPTS.md).

---

## 5. Reference file purpose

This file serves as the **single source of frontend-eng design principles** for the trainer skill. It is NOT a specialist routing trigger — it is a MINOR-versioned reference file that trainers can consult when frontend motion/animation questions arise. It does not change trainer.skill's core routing.

**L2 structure decision (2026-08-11):** Reference file (not specialist). MINOR version bump. Static-decline lifted for Phase 5+.

---

## 6. Minimal update policy

This file is updated when:
- New upstream behaviors are discovered in a future emilkowalski/skills version
- New uncovered domains emerge from trainer.skill inventory reassessment
- Trainer SemVer rules change (MAJOR bump if routing changes)

**Default: no periodic update.** The file is static until the next L2 acquisition cycle.

---

**End of references/frontend-eng.md**