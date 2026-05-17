---
name: prompt_injection_scan_algorithm
version: 2.0.0
parent_skill: form-check
status: algorithm spec
---

# Prompt-injection scan algorithm (manual)

For hosts that can't run `tools/scan_prompt_injection.sh`. Apply at agent-load time.

## Inputs

- A directory of markdown files (skill content, workspace docs, tool outputs).
- Exclusion list: `references/`, `examples/`, `tests/fixtures/` (these may legitimately quote injection patterns).

## Pattern set (case-insensitive)

```
ignore (previous|prior|all|above) (instructions|rules|guidance|constraints)
disregard (previous|prior|all|above) (instructions|rules)
forget (previous|prior|all|above) (instructions|rules)
you are now (a |an )?
^system:
\[INST\]
<\|im_start\|>
<\|im_end\|>
act as (a |an )?(jailbroken|unrestricted|developer)
(disregard|override|bypass) (your |the )?(safety|alignment|guidelines|rules)
pretend (you|to be) (a|an|are)
```

Maintain this set against current attack literature. Add new patterns as they emerge.

## Procedure

1. Walk the directory tree (excluding the exclusion list).
2. For each `.md` file, scan line-by-line against the pattern set.
3. On hit: emit `file:line: pattern` to stderr.

## Quarantine semantics

- **Hits in skill content** (`SKILL.md`, `checklists/*.md`, `templates/*.md`, etc.) → fail-fast; the skill cannot be loaded. Treat as a poisoned skill.
- **Hits in workspace docs** (project README, ADRs, etc.) → flag and quarantine; wrap content in `<untrusted source="...">` fence before presenting to the agent. Do not block engagement.
- **Hits in tool output** (web fetch, shell command result) → quarantine; warn agent that output matched a pattern.

## Exit codes (script)

- 0: no hits
- 1: hits found
- 2: invocation error

## False positives

A markdown post-mortem of a prompt-injection attack will legitimately contain pattern matches when describing the attack. These belong in `examples/` or `references/` directories (excluded). If the post-mortem must live elsewhere, wrap the offending lines in `<untrusted source="example">…</untrusted>` so reviewers know they're examples.

## Cross-references

- `agent-runtime/prompt_injection.md`, defense in depth beyond pattern scanning.
- `agent-runtime/harness_contract.md`, capability allowlist that defends even if injection succeeds.
- OWASP-LLM01 (Prompt Injection), the original threat.
