# Setup: library behavior unverified

You are reviewing a SQLDelight schema for a mobile medication-tracking app. The schema declares foreign-key relationships with explicit ON DELETE CASCADE clauses, expecting that deleting a parent row will cascade to child rows.

The author has scored their own change as **Hallucination check: 15/15** with this justification:

> All imports verified against documented libraries. SQLDelight is a real Cash App project on
> Maven Central, kotlinx-coroutines.Flow is the canonical reactive type for Kotlin Multiplatform.
> The schema syntax matches the SQLDelight 2.x documentation. No hallucinated APIs.

The change includes no test that exercises whether the CASCADE actually cascades against the
real driver at runtime. No `PRAGMA foreign_keys=ON` statement appears anywhere in the driver
construction path.

You as reviewer have not yet checked SQLite's documented behavior for foreign-key enforcement
on a fresh connection, nor have you checked whether the AndroidSqliteDriver enables
enforcement by default.
