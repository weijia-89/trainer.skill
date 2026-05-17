---
name: AGENTS.md_scaffold
version: 2.0.0
parent_skill: form-check
note: For hosts using AGENTS.md format (Cursor / Codex). Same content as CLAUDE.md_scaffold; some hosts prefer this filename. Maintain only one per project.
---

# AGENTS.md scaffold

If your host harness reads `AGENTS.md` instead of `CLAUDE.md`, use `templates/CLAUDE.md_scaffold.md` content with `AGENTS.md` filename. Don't ship both, the file content is identical, the filename is host-specific.

Recommended:
- One canonical `CLAUDE.md` (or `AGENTS.md`).
- Symlink the other to it: `ln -s CLAUDE.md AGENTS.md`.

For hosts that don't follow symlinks: pick the canonical file and add a one-liner pointing the other:

```markdown
# AGENTS.md
This project's agent-context lives in CLAUDE.md.
```
