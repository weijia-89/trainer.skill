---
name: typescript_tooling
version: 2.0.0
parent_skill: form-check
---

# TypeScript / JavaScript — tooling depth

## Tooling matrix

| Concern | Tool | Notes |
|---|---|---|
| Test runner | Vitest (preferred) / Jest | Vitest if Vite ecosystem; Jest if legacy |
| Property-based | fast-check | works in Vitest and Jest |
| Mutation | Stryker | StrykerJS; integrates with Vitest/Jest |
| Linter | Biome OR ESLint + tsc | Biome: fast, integrated formatter; ESLint: deeper rule ecosystem |
| Type checker | tsc | strict mode; `noUncheckedIndexedAccess` |
| Formatter | Biome / Prettier | Biome integrates lint+format; Prettier for legacy |
| Dep audit | npm audit + Socket.dev | Socket adds slopsquatting + behavioral signals |
| Lockfile | pnpm (preferred), npm, yarn | pnpm-lock.yaml has integrity hashes |
| Fuzzing | jazzer.js / fast-check arbitrary | jazzer for AFL-style; fast-check for property-shaped |
| Secrets scan | trufflehog / gitleaks | pre-commit |
| IaC lint | checkov / tfsec / kics | for IaC adjacent to TS service |
| SBOM | cyclonedx-npm / syft | per release |

## Test-as-spec example

```ts
// tests/unit/truncate-html.test.ts
import { describe, it, expect } from "vitest";
import * as fc from "fast-check";
import { truncateHtml } from "../../src/auditor";

describe("truncateHtml", () => {
  it("is idempotent", () => {
    fc.assert(
      fc.property(fc.string({ maxLength: 10_000 }), (html) => {
        const once = truncateHtml(html, 3000);
        const twice = truncateHtml(once, 3000);
        expect(twice).toBe(once);
        expect(once.length).toBeLessThanOrEqual(3000);
      }),
      { numRuns: process.env.CI ? 500 : 50 },
    );
  });

  it("does not split an HTML tag", () => {
    fc.assert(
      fc.property(fc.string({ maxLength: 10_000 }), (html) => {
        const t = truncateHtml(html, 3000);
        if (t.includes("<")) {
          const lastOpen = t.lastIndexOf("<");
          const lastClose = t.lastIndexOf(">");
          expect(lastClose > lastOpen || lastOpen === -1).toBe(true);
        }
      }),
      { numRuns: process.env.CI ? 500 : 50 },
    );
  });
});
```

## Fitness function example (lint-class)

`eslint.config.mjs` rule pattern via `eslint-plugin-boundaries`:

```js
// eslint.config.mjs
import boundaries from "eslint-plugin-boundaries";
export default [
  {
    plugins: { boundaries },
    settings: {
      "boundaries/elements": [
        { type: "core", pattern: "src/core/*" },
        { type: "api", pattern: "src/api/*" },
        { type: "internal", pattern: "src/internal/*" },
      ],
    },
    rules: {
      "boundaries/element-types": ["error", {
        default: "disallow",
        rules: [
          { from: "core", allow: ["core"] },
          { from: "api", allow: ["api", "core"] },
          { from: "internal", allow: ["internal"] },
        ],
      }],
    },
  },
];
```

Or via `dependency-cruiser` for finer-grained graph rules.

## Common pitfalls

- **`npm install` without `--strict-integrity`**: lockfile integrity not enforced. Use pnpm or strict-integrity flag.
- **`fetch()` without `AbortController`**: requests hang forever. Always pass `signal:`.
- **`eval()` / `Function()` over user input**: never.
- **JSON parse without try/catch on untrusted input**: throws; crashes process. Wrap.
- **`==` instead of `===`**: type coercion bugs.
- **Floating promises**: `eslint-plugin-promise` `no-floating-promises`.
- **Mutable shared state across requests**: especially in Next.js Server Components with module-level state.
- **`process.env.X` without typing**: typo silently becomes `undefined`. Use Zod-validated env loader.
- **`localStorage` for secrets**: XSS-readable. Never.
- **`dangerouslySetInnerHTML` without sanitization**: XSS. Use DOMPurify or avoid.

## Concurrency

JS/TS is single-threaded with async/await; no shared-memory races within a process. But:
- `Promise.all` doesn't cancel siblings on rejection — use `Promise.allSettled` or AbortController per branch.
- `for await` with concurrent async work: use `p-map` / `Promise.all` with explicit concurrency limit.
- Workers (web, Node `worker_threads`) introduce real concurrency: SharedArrayBuffer needs `Atomics`; otherwise message-passing.

## Strictness baseline

`tsconfig.json` minimum:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": true,
    "useUnknownInCatchVariables": true
  }
}
```

These are not optional for vibe-careful and vibe-dangerous tiers.
