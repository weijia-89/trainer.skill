---
name: runbook_supply_chain_compromise
version: 2.0.0
parent_skill: form-check
voice: imperative; assume incident is active
trigger: vendor advisory (Wiz / Aikido / Snyk / Socket / CISA / GitHub Advisory) names a package in your dep graph; OR your CI breaks with a known Shai-Hulud / typosquat signature
---

# Runbook, Supply-Chain Compromise (Shai-Hulud-class)

> P0. Run two-up, pair an engineer with a security responder. Do not run solo.
> Reference incidents: Shai-Hulud (Sept 2025), Shai-Hulud 2.0 (Nov 2025), Mini Shai-Hulud (May 2026, first cross-ecosystem npm + PyPI).

## Pre-flight

- [ ] Pair confirmed (you + security responder + on-call engineer)
- [ ] Incident channel opened: `#incident-{{ts}}-supply-chain`
- [ ] Status page status set to "investigating" (do not over-promise)
- [ ] Postmortem ticket created: `INC-{{N}}`

## Step 1, Identify

Check current vendor advisories and your dep graph:

```bash
# Pull the latest advisories
curl -sL https://www.wiz.io/blog | grep -i "shai-hulud" | head
# (Wiz, Aikido, Snyk, Socket maintain the canonical incident lists; CISA aggregates.)

# Your dep graph
pip-audit -r requirements.txt --strict
npm audit --audit-level=moderate
govulncheck ./...
cargo audit
```

Cross-reference any matches with the vendor advisory's IOC (indicators of compromise) list.

Record findings in incident channel.

## Step 2, Contain

If a confirmed compromised package is in your graph:

```bash
# Halt CI / CD immediately
{{ci-tool}} pause   # or revoke the workflow's tokens

# Block new deploys at the platform
{{deploy-tool}} freeze
```

Do **not** redeploy until eradication is complete.

## Step 3, Rotate ALL tokens

Shai-Hulud's whole purpose is exfil tokens. Assume every token in your CI namespace is compromised.

- [ ] npm tokens: revoke + reissue (npmjs.com → Account → Access Tokens)
- [ ] PyPI tokens: revoke + reissue
- [ ] crates.io tokens: revoke + reissue
- [ ] Maven Central GPG keys: rotate (audit signatures of recent releases)
- [ ] GitHub PATs (every team member; especially "deploy" or "release" PATs)
- [ ] GitHub Actions OIDC tokens: force-revoke
- [ ] CI secrets in GitHub Actions / CircleCI / GitLab / Buildkite: rotate every secret
- [ ] Cloud provider tokens (AWS / GCP / Azure access keys touching CI)
- [ ] Container registry tokens (GHCR / ECR / Artifact Registry / Docker Hub)
- [ ] Database credentials reachable from CI
- [ ] Kubernetes service account tokens
- [ ] Vault / Secrets-Manager tokens
- [ ] Any third-party API keys (Sentry, PostHog, OpenAI / Anthropic, Stripe-test, etc.)

Update audit log. **Use a fresh, isolated workstation for rotations**, do not rotate from a possibly-compromised dev machine.

## Step 4, Audit GitHub for exfil repos

```bash
gh api -X GET search/repositories \
  -f q="org:{{your-org}} Shai-Hulud in:name,description"
gh api -X GET search/repositories \
  -f q="user:{{maintainer-username}} Shai-Hulud in:name,description"
```

Repeat for every member of your org. Found repos: capture names + creation timestamps for the postmortem; report to GitHub abuse team; delete.

## Step 5, Re-scan artifacts

```bash
# Scan recent built artifacts for the malicious post-install signatures
{{vendor-provided-detection-script}}

# Scan node_modules / site-packages / vendored deps locally
find . -name "package.json" -path "*/node_modules/*" \
  -exec grep -l "<malicious-signature>" {} \;
```

If any artifact is contaminated, treat as not-shippable. Do not roll forward; rebuild from clean source.

## Step 6, Recover

Pin compromised packages to the last known-good version. Update lockfile.

```bash
# Example pattern
pnpm update {{pkg}}@{{good-version}} --strict-integrity
uv lock --upgrade-package {{pkg}}=={{good-version}} --generate-hashes
```

Re-run full CI in a clean environment. Confirm green before resuming deploys.

## Step 7, Customer communication

If exfiltration likely affected customer data: per breach-notification policy. Use this template:

```
We detected a supply-chain compromise affecting {{package}} on {{date}}.
Our investigation indicates {{scope}}.
Affected customers: {{list / criteria}}.
Action required: {{rotate any keys you stored with us / no action needed}}.
Timeline of our response: {{summary}}.
Postmortem: published at {{date}}.
```

If exfiltration did not affect customer data: a transparency post may still be appropriate. Confer with security responder.

## Step 8, Postmortem

Within 5 business days:
- Root cause analysis
- Timeline (detection → containment → eradication → recovery)
- Action items (CI architectural changes, token-isolation improvements, dep-pinning policy updates)
- "What went well / what didn't", blameless

Filed at `docs/postmortems/{{date}}-supply-chain.md`.

## After the incident, preventive actions

These should already be in place. If they aren't, this is the action-item set:

- Pin all deps with hashes
- Enforce 2FA on all registry accounts
- Use OIDC federation instead of long-lived PATs where possible
- Separate CI tokens per pipeline (do not share a master token across all CI)
- Add a "new-dep" PR template requiring slopsquatting check
- Subscribe to Wiz, Aikido, Socket, Snyk advisory feeds
- Schedule quarterly token rotation
- Add a runbook practice drill (yearly)

## Anti-patterns

- Single shared "ci-deploy-token" used across pipelines, single compromise compromises everything.
- Long-lived PATs with broad scope, should be OIDC federation or short-lived.
- "We'll rotate later", Shai-Hulud propagates within minutes; later is too late.
- Communicating before containment, adversary uses the time.
- Rotating tokens from a possibly-compromised machine, defeats the rotation.
