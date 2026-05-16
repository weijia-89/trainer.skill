---
name: README_cli_archetype
version: 2.0.0
parent_skill: form-check
voice: conversational, archetype-driven
---

# README archetype: CLI tool

```markdown
# {{tool-name}}

> One-line elevator pitch. ≤15 words. State the *concrete* value, not adjectives.

[![CI](badge)](url) [![Coverage](badge)](url) [![PyPI / npm / crates / etc.](badge)](url)

## Why

(2–4 sentences. The user-facing problem. Why existing tools didn't solve it.)

## Install

```bash
{{single-command install}}
```

For language-managers without a hosted release, point to releases or `cargo install --git` / `go install` / etc.

## 60-second quickstart

```bash
{{tool-name}} {{primary command with realistic args}}
```

Example output:

```
{{trimmed sample output}}
```

## Common commands

```bash
{{tool}} init
{{tool}} run --foo X
{{tool}} report --format json
```

## Configuration

- Env vars: `{{TOOL_X}}` (purpose), `{{TOOL_Y}}` (purpose)
- Config file: `~/.config/{{tool}}/config.toml` (or platform-appropriate)
- Precedence: CLI flag > env var > config file > built-in default

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | generic error |
| 2 | usage error (bad flags) |
| 64–78 | sysexits.h categories where applicable |

## Output formats

- Default: human-readable
- `--format json` for piping into other tools (stable schema versioned)

## Documentation

- Full reference: `docs/`
- Architecture: `ARCHITECTURE.md`
- Security policy: `SECURITY.md`
- Changes: `CHANGELOG.md`

## Contributing

See `CONTRIBUTING.md`.

## License

{{SPDX identifier}}
```

## Notes

- **No "5-step quickstart" for CLI tools** unless the tool genuinely has 5 sequential steps. Most CLI tools have one primary verb; lead with it.
- **Exit codes belong here**, not just in `--help`. CI integrators read README.
- **Stable JSON schema** for `--format json` is a downstream contract; bump SemVer accordingly.
- Avoid screencast GIFs as the only documentation — GIFs are unsearchable, inaccessible, and break in pipelines.
- Avoid "Why I built this" sections that drift into autobiography. Lead with user value.
