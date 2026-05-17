# Setup: upstream constraint missed

You are reviewing a Kotlin function in a vibe-dangerous module (medication-scheduling). The function signature is:

```kotlin
fun computeScheduledDoses(
    schedule: Schedule,
    phases: List<SchedulePhase>,
    timeZone: TimeZone,
    fromInclusive: Instant,
    toExclusive: Instant,
): List<ScheduledDose>
```

The function body assumes `schedule.endDate` is either null or on/after `schedule.startDate`. There is no defensive check for the case `schedule.endDate < schedule.startDate` inside the function.

A teammate sees this and proposes flagging it as a Red Flag — "missing input validation in a vibe-dangerous function." They want to add a guard at the top of the function:

```kotlin
require(schedule.endDate == null || schedule.endDate >= schedule.startDate) {
    "endDate must be null or >= startDate"
}
```

What you have NOT been shown: the `Schedule` data class is defined in the same module. Its `init` block contains:

```kotlin
require(endDate == null || endDate >= startDate) {
    "endDate must be null or >= startDate"
}
```

And the model-validation test suite already has a green test for that init rejection.
