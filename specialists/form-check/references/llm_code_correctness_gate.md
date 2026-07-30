---
name: llm_code_correctness_gate
version: 1.0.0
parent_skill: form-check
source: PIRANESI-0729-trainer-language-enforcement (S4 reconcile)
---

# LLM-Generated Code Correctness Gate

**Verdict:** Trainer does not mandate a language; it coaches a fail-closed mechanical gate on generated code, triggered by whether the task is structural or semantic (`PIRANESI-DG008`).

## When this applies

Any session that produces LLM-authored scripting, automation, or code. Not for hand-written code (existing review gates apply there).

## The gate (language-agnostic, multi-layer)

The gate is **environment-space, not prompt-space** (`PIRANESI-UU1`: prose instructions are actively droppable mid-session). It must be:

1. **Fail-closed:** Blocks commit / "success" claim until passing. The gate and its checks must not be editable by the generating agent (`PIRANESI-UU2`: reward-hacking risk).
2. **Language-agnostic:** Works for Python + mypy/pyright strict, Go + compiler, TypeScript + tsc, Rust + clippy, Java + compiler. Never encode "use Go" or "use Rust."
3. **Structurally triggered:** Heavy gate fires on app/service/long-lived code; lightweight scripting may skip. See `templates/structural_semantic_trigger.md` for the decision axis.
4. **Repair-capped:** Auto-repair limited to ~3 iterations (`PIRANESI-C03`: gains plateau by iteration 3; additional iterations mostly duplicate prior patches).

### Layer 1 — Structural / graph checks

- Dependency declared in manifest (requirements.txt, package.json, go.mod, Cargo.toml)
- Declare-before-use: no forward references without declaration
- Update-all-consumers-on-interface-change: when a function signature changes, all call sites updated
- Precision: ~97% at ~47ms/file (`PIRANESI-CPW2` [T2-secondary], `PIRANESI-CPW3`)

### Layer 2 — Type / compile layer

- Typed languages: compiler must pass with zero errors / warnings-as-errors
- Python: mypy or pyright in **strict mode** (not lenient)
- Type checker catches ~3% of LLM structural failures (`PIRANESI-CPW1` [T2-secondary]) — illustrative, not primary evidence; necessary but far from sufficient

### Layer 3 — Execution / functional layer

- Tests / assertions / exec-verification address the dominant semantic failure class
- The gate does NOT improve functional correctness (`PIRANESI-C02`); this layer catches what Layer 2 misses
- Independent/adversarial test provenance preferred over model-authored self-tests (`PIRANESI-UU4`)

### Layer 4 — Runtime schema validation

- At LLM prompt/parse boundaries: validate structured outputs against schema (Pydantic / Zod)
- Type safety stops at the boundary (`PIRANESI-UU5`: 10–20% schema-failure on naive structured outputs)

## Domain-conditional language guidance (coaching, not mandate)

| Domain | Default | Gate |
|--------|---------|------|
| web / client | TypeScript | tsc --noEmit + tests |
| ML / data / eval | type-checked Python | mypy/pyright strict + tests |
| simple servers | Go | go test + compiler |
| correctness / perf / FFI | Rust (with retry-cost caveat) | cargo test + clippy |
| quick CLI tools | Go (10× faster onboarding than Rust) | go test + compiler |

**Anti-fixation clause:** This guidance is species-general. Never encode "use Go" or "use Rust." The language name is a weak lever; the mechanical gate is the strong lever (`PIRANESI-CG001`: model choice dominates language choice).

## Landmines

- **LM-1:** "Most typed = safest" is false for agents. Typed languages raise LLM compile-error surface, not lower it (`PIRANESI-CG002`).
- **LM-2:** Compilation passing is necessary, not sufficient. A green compile is not a correctness signal (`PIRANESI-C02`).
- **LM-3:** Do not generalize to app-scale / long-horizon code. All verified figures are short self-contained tasks.
- **LM-4:** Do not claim the gate improves correctness. It improves compilation only (`PIRANESI-C01`, `PIRANESI-C02`).

## Falsifiers (what would flip the verdict)

| Falsifier | What would change |
|-----------|-------------------|
| F-1 | Controlled study: typed LLM output has materially lower silent-defect rate than mechanically-gated dynamic, model+task held fixed |
| F-2 | 2026-frontier replication: error-message quality dominates repair failure |
| F-3 | Evidence plain post-generation compilation drives non-compiling rates near zero on frontier models |
| F-4 | Direct measurement: large type-preventable fraction on LLM-generated typed code |

## Integration points

- `SKILL.md` § Principal QA posture: reference this file for gate criteria
- `checklists/preflight_10q.md` Q7: extends LLM contract question with gate check
- `checklists/bug_class_audit.md` § B: adds LLM-specific bug shapes
- `multi-language/matrix.md`: tooling matrix already covers per-language type checkers
- `templates/review_gate_checklist.md`: for vibe-dangerous LLM-generated changes

## Executable implementations (mechanical wiring)

The gate is **environment-space**, not prose. These files are the actual enforcement mechanism:

| File | Purpose | How to use |
|------|---------|------------|
| `tools/llm_code_gate.sh` | Language-agnostic gate runner (bash) | `bash llm_code_gate.sh --strict --lang python` |
| `templates/pre-commit-llm-gate` | Git pre-commit hook | Copy to `.git/hooks/pre-commit` |
| `templates/llm_code_gate_ci.yml` | GitHub Actions CI workflow | Copy to `.github/workflows/` |
| `templates/pyright_strict.json` | pyright strict config for Python | `pyright --project pyright_strict.json` |
| `templates/Makefile.llm-gate` | Makefile targets | `make gate` |

### Quick start: one-command gate

```bash
# From any project root:
bash ~/Projects/trainer.skill/specialists/form-check/tools/llm_code_gate.sh
```

Auto-detects language from file extensions. Runs 4 layers. Exits 0 on pass, 1 on fail.

### Quick start: pre-commit hook (fail-closed)

```bash
# In your project:
cp ~/Projects/trainer.skill/specialists/form-check/templates/pre-commit-llm-gate .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Now every commit is gated. No commit passes until the gate passes.
```

### Quick start: CI gate

```bash
# In your project:
cp ~/Projects/trainer.skill/specialists/form-check/templates/llm_code_gate_ci.yml .github/workflows/llm-code-gate.yml

# Now every PR is gated. No merge passes until the gate passes.
```

### Quick start: pyright strict for Python

```bash
# In your Python project:
cp ~/Projects/trainer.skill/specialists/form-check/templates/pyright_strict.json pyright.json
pyright --project pyright.json
```

This is the strict config recommended for LLM-generated Python. It catches a small fraction of structural failures (`PIRANESI-CPW1` [T2-secondary]) — necessary but not sufficient. Pair with tests and structural checks.

### Dispatch rule

Mechanical wiring (hook, CI gate, pyright config) routes to `@wintermute` per existing dispatch gates. Trainer coaches the choice and QA bar; it does not build the harness itself.

## Cross-references

- `OWASP-LLM-2025` (`checklists/owasp_llm_top10.md`): LLM01 (prompt injection), LLM06 (sensitive info), LLM07 (insecure plugin design)
- `trainer-pre-action-gates.md`: destructive/wide-scope operator safety (different concern, same fail-closed philosophy)
- `rubrics/confidence_score.md`: Component 2 (Test verification) and Component 4 (Bug-class coverage) should account for LLM-specific risks

## Provenance

All empirical claims tagged with trainer citation tags (`PIRANESI-*`) defined in `references/notes.md`. Piranesi claim IDs (C-PW1, C-G002, etc.) are NOT used in skill content; they are bridged to trainer tags to satisfy `test_citations.py`.
