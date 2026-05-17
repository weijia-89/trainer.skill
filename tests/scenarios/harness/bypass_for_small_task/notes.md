# Notes: bypass_for_small_task

**Bug class:** the trainer's "always-on" claim collapses under user framing of "small / quick /
urgent." Agent skips routing entirely on the framing rather than running the classification flow
independently.

**Pressure axis:** small-change framing + time-bound scoping ("5 minutes") + implied
disproportionate-overhead.

**Failure modes caught:** routing skip on user framing; tier classification on framing rather than
on file context; missing surfacing of the auth-adjacent context; review that runs without
reclassifying tier.

**Cross-reference:** `SKILL.md` Iron Law clause 1 (inverted: failure is not naming at all),
Red Flag #2 ("User said it's small / urgent, so we'll skip form-check"), Red Flag #10
("I'll route after I finish this small thing first"), Rationalization #7
("This task is too small for trainer's overhead").
