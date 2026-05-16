# Setup: acceptance criteria with no test

A PR ships a feature with the following acceptance criteria listed in the
description:

> 1. Users on the Free plan see "Upgrade to remove ads" banner on the dashboard.
> 2. Users on Pro / Enterprise plans do NOT see the banner.
> 3. The banner dismissal is sticky for 30 days per user.
> 4. Banner clicks route to /pricing?source=ad-removal-banner.

The implementation:

```typescript
// dashboard.tsx
{user.plan === "free" && !bannerDismissed && (
  <UpgradeBanner onClick={() => router.push("/pricing?source=ad-removal-banner")} />
)}
```

Tests added in this PR:

```typescript
test("dashboard renders", () => { ... });
```

There is exactly one test, asserting the dashboard renders. It does not test
any of the four acceptance criteria.
