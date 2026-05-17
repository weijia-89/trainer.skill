---
name: owasp_llm_top10
version: 2.0.0
source: OWASP-LLM-2025 (v2.0, Nov 2024)
url: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
---

# OWASP Top 10 for LLM Applications (2025), review checklist

Apply to any code that calls an LLM, agent runtime, or vector DB. Each item: question + sample defense.

## LLM01:2025, Prompt Injection

**Question**: Does any user-controllable input reach the LLM via prompt template, RAG retrieval, tool output, or system message?

**Sample defenses**:
- Treat all model inputs from untrusted sources as data, not instructions. Wrap in `<untrusted source="user">…</untrusted>` fences.
- Validate model output against a strict schema (Pydantic / Zod). Reject and retry on schema violation.
- Use structured outputs (function calling / tool use) instead of free-text whenever possible.
- Apply allowlist on tool invocations the model can request (see `agent-runtime/harness_contract.md`).
- For RAG: scan retrieved chunks for prompt-injection patterns at retrieval time (`tools/scan_prompt_injection.sh`).

**Anti-pattern**: concatenating user input directly into the system prompt.

## LLM02:2025, Sensitive Information Disclosure

**Question**: Does the model have access to data that shouldn't be revealed in its outputs?

**Sample defenses**:
- Per-tenant context isolation (no shared system prompts across tenants).
- Output redaction layer (PII / secret / API key patterns).
- Rate-limit and audit-log queries to detect extraction attempts.
- For fine-tuned models: training-data review for memorized PII; differential privacy where applicable.

## LLM03:2025, Supply Chain

**Question**: Where do model weights, embeddings, fine-tuning data, and prompt templates come from? Are they versioned and integrity-checked?

**Sample defenses**:
- Pin model versions explicitly (no "latest"). Record in CLAUDE.md / AGENTS.md.
- Verify model provenance (Hugging Face SHA, signed checkpoints where available).
- Treat third-party prompt templates as untrusted dependencies, vuln-scan and pin.
- For agentic tools: vuln-scan tool implementations as you would for npm/pip deps.

## LLM04:2025, Data and Model Poisoning

**Question**: Could an attacker poison training data, RAG corpus, or fine-tuning input?

**Sample defenses**:
- Provenance tracking on all training / RAG corpus inputs.
- Anomaly detection on training-data distribution.
- For RAG: source-trust scoring; never index unsigned content.

## LLM05:2025, Improper Output Handling

**Question**: Does downstream code execute or render LLM output?

**Sample defenses**:
- Treat output as untrusted user input. Sanitize before rendering (XSS), parameterize before SQL, never `eval()` model output.
- Enforce JSON schema before action; reject non-conforming output.
- For tool-calling: validate every tool-call argument before invocation.

## LLM06:2025, Excessive Agency

**Question**: Does the agent have more capability than its task requires?

**Sample defenses** (full spec: `agent-runtime/harness_contract.md`):
- Capability allowlist tiered by vibe-safety (vibe-dangerous → no shell-write, no DB-write, no network-write).
- Human confirm for any irreversible op (file delete, DB write, public posting).
- Tool-call ledger (`.agent/ledger.jsonl`) reviewed before merge.
- Scope confinement to git worktree, not main.

## LLM07:2025, System Prompt Leakage

**Question**: Could the model leak its system prompt or instructions?

**Sample defenses**:
- Don't put secrets / API keys / sensitive instructions in the system prompt. Pass via tool calls instead.
- Treat system-prompt leakage as a likelihood, not a possibility.
- If the system prompt encodes business rules, also enforce them server-side; do not rely on the prompt as the only gate.

## LLM08:2025, Vector and Embedding Weaknesses

**Question**: Are embeddings or vector DBs trusted as authoritative? Could poisoned embeddings change retrieval?

**Sample defenses**:
- Source-track embeddings: log which corpus chunk produced which vector.
- Versioning on embedding model, re-embed on model upgrade; treat as a migration.
- Rate-limit embedding queries to detect extraction attempts.

## LLM09:2025, Misinformation

**Question**: Does the application present model output as fact without verification?

**Sample defenses**:
- For factual claims: ground via RAG with cited sources; surface citations to the user.
- Confidence flags on output (model uncertainty signals).
- Human-in-the-loop review on high-stakes domains (medical, legal, financial).

## LLM10:2025, Unbounded Consumption

**Question**: Can a user trigger arbitrarily expensive model calls?

**Sample defenses**:
- Per-tenant rate limits (requests + token budget).
- Timeouts on every model call. Cancel on user disconnect.
- Maximum context-window budget enforced before send.
- Cost-based quotas with alerting.

## Cross-references

- Capability allowlist + ledger + rollback: `agent-runtime/harness_contract.md`
- Prompt-injection scanning: `agent-runtime/prompt_injection.md`
- Supply chain: `checklists/supply_chain_slsa.md`
- Data classification (LLM02 + LLM04): `templates/threat_model.md`

## Output

For each item: write a P0/P1/P2 finding row in the review report. Cite the LLM0N:2025 ID.
