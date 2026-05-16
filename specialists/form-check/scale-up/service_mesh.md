---
name: service_mesh
version: 2.0.0
parent_skill: form-check
gate: forcing-constraint-required
---

# Service Mesh

> **[GATED — informational only]** Forcing-constraint ADR required.
>
> Service mesh is operational tax. Most "we need a service mesh" conversations are solved by mTLS + a single ingress + good service discovery — without the mesh's deployment, certificate-management, and debugging burden.

## When this chapter applies

- ≥50 services AND mesh-required policy (e.g. zero-trust mandate per regulator, or compliance attestation requiring mTLS-everywhere with SPIFFE-style identity)
- Existing platform team capable of operating the mesh
- Not when: "we want zero-trust" without naming the threat-model that monolith + ingress mTLS doesn't address

## Mesh choices (current generation)

| Mesh | Strength | Weakness |
|---|---|---|
| Istio | feature-rich; mature | operationally complex; sidecar latency tax |
| Linkerd | simpler; lower latency tax | smaller feature set |
| Cilium (eBPF) | kernel-level performance; emerging features | newer; smaller operator pool |
| AWS App Mesh / GCP ASM | cloud-managed; smaller scope | vendor lock-in |

## What a mesh provides

- **mTLS between services** (SPIFFE identity)
- **Traffic policy** (canary, blue-green, retries, timeouts at the mesh layer)
- **Observability** (auto-emitted metrics + traces; some L7 protocol intelligence)
- **Authorization policy** (per-service, per-method)

## What a mesh costs

- Operational team (≥1 FTE for a non-trivial deployment)
- Sidecar latency tax (Istio: ~1–5ms per hop; Linkerd: ~0.5–2ms; Cilium: lower with eBPF)
- Memory overhead per pod
- Debugging complexity (extra layer between application and network)
- Upgrade burden (mesh upgrades + application upgrades + control-plane upgrades)

## Cheaper alternatives (try first)

- **mTLS at ingress** (cert-manager + nginx / Envoy / Traefik) for north-south traffic
- **mTLS in application library** for east-west (e.g. Spring Cloud TLS, gRPC built-in TLS)
- **Single API gateway** for routing + retries + auth without sidecars
- **Service-to-service auth via signed JWT** with per-service identity (no mesh needed)

If these don't address your forcing constraint, *then* consider mesh.

## Anti-patterns

- Mesh as the first answer to zero-trust — mTLS at ingress + library-level mTLS east-west handles 80%.
- Multiple meshes (Istio + Linkerd in different teams) — operational nightmare.
- Mesh for traffic policy when feature flags suffice.
- Mesh for observability when OpenTelemetry libraries do it without the sidecar.
- Mesh that nobody on-call knows how to debug at 3 AM.

## Sunset

If the forcing constraint is deprecated (regulator change, scale drop), retreat to mTLS-at-ingress patterns. The migration cost is large; track it on the roadmap.

## Cross-references

- `distributed_systems.md` (decomposition prerequisites)
- `soc2_iso27001.md` (zero-trust regulatory cases)
