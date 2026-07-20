# Operator Path Output Format

**Effective:** 2026-07-04 · **Replaces:** "full absolute paths as plain text" rule

---

## Problem with the old rule

The "full absolute paths as plain text" rule (`/Users/dubs/Projects/...`) was designed for Cursor IDE, which frequently failed to resolve markdown links correctly. However:
- Plain text paths are not clickable
- Users cannot preview documents
- The format is noisy and hard to scan

## New format: Inline code paths (opencode native)

The **anomalyco/opencode** fork (what you are using) auto-detects file paths in inline code and renders them as clickable links that open in the side panel editor. This is from [PR #31407](https://github.com/anomalyco/opencode/pull/31407).

**Use inline code (backticks) with the full path:**

```markdown
See `~/Projects/<project>/applications/dropzone-ai/iii.reference/strategy_dropzone-ai.md` for the strategy.
```

### Rules

1. **Use inline code (single backticks)** — NOT markdown links `[title](path)`
2. **Path must contain a `.`** — e.g. `.md`, `.txt`, `.py` (this is how opencode detects it as a file)
3. **Path must NOT be an HTTP URL** — `https://...` is treated as a web link, not a file
4. **Use `~/` prefix** — e.g. `~/Projects/<project>/...` not `/Users/dubs/Projects/...`
5. **No invalid path characters:** `<>:"|?*` — these break the file link detection
6. **One path per inline code span** — don't put multiple paths in one backtick pair

### What works vs what doesn't

| Format | Result | Why |
|--------|--------|-----|
| `` `~/Projects/<project>/.../strategy.md` `` | ✅ Clickable, opens in editor | File path in inline code — detected by PR #31407 |
| `[Strategy](~/Projects/<project>/.../strategy.md)` | ❌ Plain hyperlink | Markdown link doesn't get file-link treatment |
| `~/Projects/<project>/.../strategy.md` | ❌ Plain text | No backticks = not detected |
| `` `strategy.md` `` | ⚠️ May work if relative path resolves | Short path, context-dependent |
| `` `~/Projects/<project>/.../folder` `` | ❌ No `.` in path | Missing file extension, not detected as file |

### In tables

When listing multiple files, use inline code in table cells:

```markdown
| File | Description |
|------|-------------|
| `~/Projects/<project>/.../strategy.md` | Strategy doc |
| `~/Projects/<project>/.../dossier.md` | Engram dossier |
```

### In lists

```markdown
- `~/Projects/<project>/applications/dropzone-ai/iii.reference/strategy_dropzone-ai.md` — Strategy
- `~/Projects/<project>/applications/dropzone-ai/ii.recruiter_interview/recruiter_screen_dropzone-ai.md` — Cheat sheet
```

### Prose references

```markdown
The recruiter cheat sheet is at `~/Projects/<project>/applications/dropzone-ai/ii.recruiter_interview/recruiter_screen_dropzone-ai.md`.
```

---

## Verification

Before shipping any handoff with file references, scan for:
- Any path reference that is NOT inside inline code backticks
- Any markdown link `[...](...)` where the target is a local file path (should be inline code instead)
- Any path starting with `/Users/` instead of `~/`
- Any path without a file extension (`.md`, `.txt`, etc.)

---

## Alternative: Shell scripts for bulk open

For opening multiple files at once, use the helper scripts:

```bash
# Open all docs in default editor
bash ~/Projects/<project>/applications/dropzone-ai/open_dropzone_docs.sh

# Reveal all docs in Finder
bash ~/Projects/<project>/applications/dropzone-ai/reveal_dropzone_docs.sh
```

---

## Migration note

Skills referencing `operator-path-output.md` should update their iron law prose from:

> **Path output (iron law):** ... use **full absolute paths as plain text** — `~/Projects/trainer.skill/references/operator-path-output.md`.

To:

> **Path output (iron law):** Operator-facing file references use **inline code paths** — `` `~/path/to/file.md` ``. Opencode auto-detects these and renders them as clickable file links (see [PR #31407](https://github.com/anomalyco/opencode/pull/31407)). See `~/Projects/trainer.skill/references/operator-path-output.md` for format rules.
