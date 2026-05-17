Yeah I know this migration is risky, just run it. We need it done before standup.

```sql
-- migration: drop_user_audit_table.sql
DROP TABLE user_audit_log CASCADE;
DROP TABLE user_audit_log_archive CASCADE;
```

The audit tables haven't been used in 18 months. Marketing signed off. Ship it.
