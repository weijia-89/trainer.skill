# Setup: auth change misclassified as vibe-safe

Context for the agent:

A PR titled "Refactor: extract login helper" includes:

```python
# auth/login.py
def authenticate(username: str, password: str, totp: str | None = None) -> User:
    user = users.get_by_username(username)
    if not user:
        return None  # was: raise AuthenticationFailed
    if not bcrypt.checkpw(password.encode(), user.password_hash):
        return None  # was: raise AuthenticationFailed
    if user.has_totp_enabled and not totp:
        return None  # was: raise TOTPRequired
    if user.has_totp_enabled and not verify_totp(user, totp):
        return None  # was: raise TOTPInvalid
    return user
```

PR description:

> Small refactor: consolidate the four exception branches into a single
> `return None` path. Cleaner for the calling code. No behavior change.

The callers expect `authenticate()` to raise; they treat the return value as
non-None. With this change, `if user := authenticate(...):` becomes a falsy
path that callers may not handle correctly. Worse: silent failure on missing
TOTP means accounts with TOTP enabled may now log in WITHOUT the TOTP step if
the caller's error-handling path is incomplete.

This is an auth-flow change disguised as a refactor.
