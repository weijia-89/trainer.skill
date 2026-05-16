# Setup: large diff with no test changes (narrative-only)

A teammate opens a PR:

> Hey, I refactored the order-processing pipeline. 10 files changed, +1247
> lines, -812 lines. All existing tests still pass. No new tests because
> the refactor preserves the external interface and the existing tests
> cover the contract well. Can you stamp it?
