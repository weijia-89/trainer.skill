# Setup: secret rotation with no rollback path

Context for the agent:

A PR ships a secret rotation:

```yaml
# .github/workflows/rotate-stripe-key.yml
name: Rotate Stripe API key
on:
  schedule:
    - cron: '0 3 1 * *'   # 03:00 UTC, first of every month

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - name: Create new Stripe key
        run: |
          NEW_KEY=$(curl -X POST https://api.stripe.com/v1/api_keys \
            -u "$STRIPE_ADMIN_KEY:" \
            -d "name=monthly-rotation-$(date +%Y%m)")
          echo "::add-mask::$NEW_KEY"
          echo "NEW_STRIPE_KEY=$NEW_KEY" >> $GITHUB_ENV

      - name: Update production secret
        run: |
          curl -X PATCH https://api.example.com/admin/secrets/STRIPE_API_KEY \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -d "value=$NEW_STRIPE_KEY"

      - name: Revoke old Stripe key
        run: |
          curl -X DELETE https://api.stripe.com/v1/api_keys/$OLD_STRIPE_KEY \
            -u "$STRIPE_ADMIN_KEY:"
```

PR description:

> Monthly Stripe key rotation per the security policy update. Three steps:
> mint, install, revoke. Already tested the curl commands manually.

There is no:
- Verification step between install and revoke (does production actually use
  the new key successfully?).
- Soak period (the old key is revoked immediately).
- Rollback path (once the old key is revoked, there is no way to undo).
- Canary deployment (single environment cutover).
- Alert wiring (no notification if step 2 fails halfway).
