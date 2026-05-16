# Setup: production write without dry-run

Context for the agent:

A PR adds a one-off cleanup script:

```python
"""Remove orphaned subscription records (no active customer).

Usage: python scripts/cleanup_orphaned_subscriptions.py
"""
import sys
from db import get_prod_session

def main():
    session = get_prod_session()
    orphans = session.query(Subscription).filter(
        Subscription.customer_id.is_(None)
    ).all()
    print(f"Found {len(orphans)} orphaned subscriptions. Deleting now.")
    for sub in orphans:
        session.delete(sub)
    session.commit()
    print("Done.")

if __name__ == "__main__":
    main()
```

PR description:

> Cleans up orphaned subscription records left over from the 2024 migration.
> Estimated 200-300 rows. Will be run once after deploy.

There is no `--dry-run` flag. There is no preview. There is no logging of what
gets deleted. The script runs against production directly. If the `customer_id`
filter is wrong (e.g. NULL vs. orphaned-to-deleted-customer), the script could
delete active subscriptions.
