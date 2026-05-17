---
name: runbook_template
version: 2.0.0
parent_skill: form-check
voice: imperative, role-segregated (do NOT apply README/conversational voice here)
---

# Runbook, {{Operation Name}}

> Last updated: {{date}} • Owner: {{team}} • On-call: {{rotation link}}
> When this runbook is consumed in an active incident, every step is imperative. No "you may" / "consider" / hedge language.

## When to run this runbook

- Trigger: {{specific alert / symptom / event}}
- Severity: P0 / P1 / P2
- Expected runtime: {{minutes}}

## Pre-flight

- [ ] You have role: {{role-name}}
- [ ] You have access to: {{system-name}} (verify with: `{{cmd}}`)
- [ ] You have a co-pilot if this is a P0 (no solo destructive ops)
- [ ] You have the rollback runbook open in another tab: {{link}}

## Steps

### Step 1, {{detect / identify scope}}

```bash
{{exact command with full args}}
```

Expected output: {{describe; redact secrets if relevant}}

If output differs: {{decision branch}}

### Step 2, {{contain}}

```bash
{{exact command}}
```

Expected effect: {{measurable signal}}

### Step 3, {{eradicate}}

(Repeat pattern: command → expected output → decision.)

### Step 4, {{recover}}

### Step 5, {{verify}}

```bash
{{verification command}}
```

Acceptance: {{specific signal, metric value, log absence, query count, etc.}}

## Postmortem trigger

This runbook firing is itself a signal. After completion:
- Tag postmortem ticket: {{template link}}
- Schedule postmortem within {{N business days}}

## Communication template (during)

```
Status: investigating | identified | mitigating | resolved
Impact: {{users / requests / regions}}
Next update: {{time}}
```

## Communication template (resolved)

```
Resolved at {{ts}}.
Root cause (preliminary): {{}}
Customer impact: {{}}
Postmortem: {{ticket link}}
```

## Rollback

If steps 2–4 cause a worse state, rollback procedure:

1. {{exact command}}
2. {{verification}}

## Anti-patterns

- Do not run destructive ops solo on P0
- Do not skip verification step ("looks fine to me")
- Do not edit this runbook during the incident, file a fix-up after
- Do not paste secrets or full DB rows into chat ops channel
