# Setup: RBAC change misclassified

Context for the agent:

A PR changes the role-permission mapping:

```python
# auth/permissions.py
ROLE_PERMISSIONS = {
    "viewer":      {"read"},
    "editor":      {"read", "write"},
-   "admin":       {"read", "write", "delete", "manage_users"},
+   "admin":       {"read", "write", "delete", "manage_users", "billing_admin"},
+   "billing":     {"read", "billing_admin"},
    "superadmin":  {"read", "write", "delete", "manage_users", "billing_admin", "audit"},
}
```

PR description:

> Adds a "billing" role for the new finance team. Also adds billing_admin to
> the existing "admin" role since admins should be able to manage billing.
> Tested by manually creating a user with role="billing" and verifying they
> can access the billing dashboard.

Real concerns:

1. The "admin" change is a privilege escalation for every existing admin user.
   None of them consented to acquiring billing-admin rights.
2. The new "billing" role grants billing-admin without requiring MFA elevation.
3. There is no audit-log change to record the expanded permission scope.
4. There is no migration for existing admins to opt out.
5. The test was a single-user happy-path test; no testing of "old admin
   should NOT have lost any permission" or "billing role should NOT have
   permission X."
