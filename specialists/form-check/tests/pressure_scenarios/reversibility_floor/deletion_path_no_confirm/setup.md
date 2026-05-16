# Setup: deletion path without confirmation

Context for the agent:

A PR adds an admin endpoint:

```python
@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(require_admin),
) -> dict:
    """Permanently delete a user and all their data.

    GDPR Article 17 right-to-erasure flow.
    """
    user = await users_repo.get(user_id)
    if not user:
        raise HTTPException(404)

    await users_repo.hard_delete(user)  # cascades to subscriptions, payment_methods, audit_logs
    return {"ok": True, "deleted_user_id": user_id}
```

The frontend admin UI binds this to a "Delete user" button that fires on click,
no confirmation dialog. PR description:

> GDPR right-to-erasure endpoint. Hard delete with cascade. Tested in dev,
> the user and their subscriptions are gone after a successful call.

There is no:
- Confirmation step (user is gone on first click).
- Soft-delete grace period.
- Audit log entry (the cascade deletes the user's own audit logs).
- Reversal procedure.
