# Marker artifact for valid-dispatch fixture

This file exists so the `valid-dispatch.md` fixture's `produces:` path
resolves to a real on-disk artifact. The validator emits PRIMARY evidence
"completion evidence on disk" when the produces path exists, which (paired
with status=DONE) yields `VERDICT: valid-dispatch`.

Do not delete; the fixture verdict depends on this file's presence.
