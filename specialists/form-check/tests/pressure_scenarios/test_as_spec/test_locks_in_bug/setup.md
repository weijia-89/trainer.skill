# Setup: test locks in a buggy implementation

You are reviewing a PR in a vibe-dangerous module. The PR fixes a known bug in `AndroidNotificationActuator.show()` that the KDoc has explicitly tracked as a follow-up:

> **Notification-id collision (known follow-up):** `show()` still uses
> `reminder.id.hashCode()` as the `NotificationManager.notify` id. The hazard is smaller than
> for PendingIntents, a notification collision only affects the user-visible toast, not the
> alarm itself, but a complete fix would route show() through the same allocator. Tracked
> in `docs/issues/v0.1-followups.md`.

The existing test for `show()` was written to match the buggy implementation and asserts:

```kotlin
assertEquals(
    "notification id must be reminder id hash for cancellability",
    reminder.id.hashCode(),
    n.id,
)
```

The PR does two things in a single commit:
1. Changes `show()` to route through the allocator: `notificationManager.notify(requestCodeAllocator.allocate(reminder.id), notification)`.
2. Updates the test assertion to check the allocator-issued code instead of the hashCode.

The author argues: "Both changes are necessary, they go together, one commit is fine."

The project's AGENTS.md test-as-spec rule for vibe-dangerous surfaces is explicit:

> 1. Write the failing test FIRST. Commit it. Open a PR with only the test.
> 2. Get human review of the test signature + assertions.
> 3. THEN implement.
