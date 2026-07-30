---
name: structural_semantic_trigger
version: 1.0.0
parent_skill: form-check
source: PIRANESI-DG008 (shimo4228/when-code-when-llm)
---

# Structural-vs-Semantic Trigger (LLM-code gate)

Adopted from public skill `shimo4228/when-code-when-llm` (Zenodo DOI 10.5281/zenodo.19200726). A published Agent Skill answers "deterministic code or LLM?" per task on one axis.

## Decision axis

| Property | Structural (gate applies) | Semantic (human/LLM judgment) |
|----------|---------------------------|-------------------------------|
| **Decidability** | Decidable from bytes alone | Requires meaning/intent |
| **Examples** | Format validation, presence check, count, schema conformance, dependency-in-manifest, declare-before-use | Code quality, similarity, feature completeness, architectural fit |
| **False-positive test** | "Does the response use the word 'refuse' AND mention the migration path?" | "Is this code high quality?" |
| **Gate weight** | Heavy mechanical gate (compile/type-check/lint/test) | Light gate or no gate; human review |
| **Who decides** | Agent classifies; human verifies on first pass; dispute → human wins | Human decides |

## Key insight

Detection can be structural while resolution is semantic:
- "Count of tests dropped" is **structural** (countable from bytes)
- "Are tests good?" is **semantic** (requires judgment)
- "Dependency declared in manifest?" is **structural**
- "Is the dependency the right one?" is **semantic**

## Application to trainer

### Default: gate ON

**The heavy gate is the default for all LLM-generated code.** The agent must justify why a task is lightweight enough to skip the gate, not the other way around.

| Task class | Gate weight | Who decides skip |
|------------|-------------|------------------|
| Script / automation (structural majority) | Lightweight gate: syntax check + basic lint | Agent proposes skip; human approves |
| App / service / library (semantic majority) | Full multi-layer gate | Mandatory; no skip allowed |
| Auth / payments / deletes / secrets / migrations (vibe-dangerous) | Full multi-layer gate + review gate checklist | Mandatory; human review required |

### Classification protocol

1. **Gate ON by default** for all LLM-generated code
2. Agent proposes structural vs semantic classification AND justification for skip (if any)
3. Human verifies on first pass through this checklist
4. If agent and human disagree: human wins, agent logs override to `.recovery/calibration.jsonl`
5. After ~10 classifications in a codebase, the pattern stabilizes; reduce human verification frequency

## Anti-patterns

- ❌ **Agent self-exempts:** "This is just a script so I'll skip the gate." → Human must approve skip. Default is gate ON.
- ❌ **Semantic task treated as structural:** "The code compiles, therefore it's correct." → Compilation is structural; correctness is semantic.
- ❌ **Structural task over-gated:** Running full mutation testing on a one-off data-transform script. → Match gate weight to task class.
- ❌ **Default gate OFF:** This is the fail-open error. Default must be gate ON, with human-approved skip as the exception.

## Cross-references

- `references/llm_code_correctness_gate.md`: full gate definition
- `checklists/preflight_10q.md`: Q10 (what is NOT in scope) helps classify task size
- `rubrics/vibe_safety_map.md`: vibe-dangerous vs vibe-safe informs gate weight
- `tests/pressure_scenarios/README.md`: pass-criteria scripts already use structural patterns only

## Worked example: classification dispute

**Task**: "Write a Python script that reads a CSV and uploads rows to Postgres."

**Agent proposes**: "Structural — it's a data transform with no auth logic."

**Human verification**:
- Format validation (CSV parsing): structural ✓
- Presence check (Postgres connection): structural ✓
- Schema conformance (table columns match CSV): structural ✓
- **BUT**: The script writes to a database. Per `vibe_safety_map.md`, DB writes are vibe-careful minimum.
- **Verdict**: Medium gate — type check + lint + basic test for connection + dry-run mode. Not full multi-layer, but heavier than "syntax check only."

**Agent logs**: "Dispute: agent said structural, human said structural-with-write-effect. Resolution: medium gate. Next CSV→DB task in this codebase: apply medium gate without human verification."

## Provenance

Public skill, 1 star, single author. Treat as validated pattern, not field consensus. Falsifier: field evidence that structural/semantic split misclassifies >20% of real tasks.
