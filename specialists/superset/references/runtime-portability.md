# Runtime portability

The agent-prompt template assumes Cascade-on-Windsurf tool semantics. Other runners differ. This reference maps load-bearing template elements onto the major runners.

The mapping is validated for Cascade-on-Windsurf and Claude Code. Cursor, Codex, and Gemini CLI entries are best-effort drafts; verify against current runner docs before relying on them.

## Tool-name mapping

| Template element | Cascade-on-Windsurf | Claude Code | Cursor | Codex | Gemini CLI |
|---|---|---|---|---|---|
| Shell command tool | `run_command` | `Bash` | `terminal` (varies) | `shell` | `run_shell_command` |
| Working-directory param | `Cwd` (parameter) | shell `cd` then run (no isolated cwd param) | shell `cd` | shell `cd` | shell `cd` |
| File read | `read_file` | `Read` | `read_file` | `read_file` | `read_file` |
| File edit | `edit` / `multi_edit` | `Edit` | `edit_file` | `edit_file` | `replace` / `write_file` |
| File create | `write_to_file` | `Write` | `write_to_file` | `write_to_file` | `write_file` |
| Web fetch | `read_url_content` | `WebFetch` | `web_search` (varies) | `web_search` | `google_web_search` |
| Subagent dispatch | (operator opens fresh chat) | `Task` (general-purpose) | (operator opens fresh chat) | (operator opens fresh chat) | (operator opens fresh chat) |

## Cascade-on-Windsurf specifics (the default)

- `run_command` takes a `Cwd` parameter. Always use it; never `cd a && b` (safe-terminal Tier-1 #4).
- `Blocking: true` waits synchronously; combine with `WaitMsBeforeAsync: 3000-5000` for jobs that take 30 seconds to 2 minutes.
- Long-running jobs (> 2 minutes) use the `/run-long-job` workflow (detach with `nohup ... & disown`, write to a log, ping the operator back).
- `read_file` and `edit` block gitignored paths. Workaround: write a Python script to `/tmp/update_<task>.py` and run it via `run_command`.

## Claude Code specifics

- No `Cwd` parameter. Each `Bash` call starts a fresh shell. To run in a worktree, prefix every command with `cd <worktree> &&` (cannot avoid the `cd a && b` pattern that safe-terminal Tier-1 #4 forbids in Cascade).
- The `Task` tool dispatches a fresh subagent in the same chat, returning to the parent on completion. This is closer to a built-in batch-dispatch primitive than Cascade's fresh-chat model.
- Skills load via the `Skill` tool. The `Skill: superset` invocation reads `~/.claude/skills/superset.skill/SKILL.md`.
- The `TodoWrite` tool replaces Cascade's `todo_list`.

Adaptation for superset's agent-prompt template: replace `run_command` with `Bash`, drop the `Cwd` parameter callout, replace `read_file`/`edit` with `Read`/`Edit`. Worktree workflow still applies; the operator dispatches via the `Task` tool rather than opening a fresh chat window.

## Cursor specifics

- The agent operates inside the editor; `terminal` and `read_file` are the typical tools.
- No first-party subagent-dispatch primitive. Parallel batches require the operator to open separate Cursor windows or use external agent runners.
- Cursor's `.cursor/rules/*.mdc` files load on session start. superset can be loaded as an `always_apply` rule pointing at the canonical `SKILL.md`.

## Codex specifics

- Codex agents typically run as one-shot CLI calls or within ChatGPT's agent mode.
- Worktree workflow applies, but the operator coordinates between agent invocations rather than within a chat.
- The `--allowedTools` flag (where present) gates which tools the agent can call; superset needs at minimum shell + file-read + file-write.

## Gemini CLI specifics

- Skills activate via the `activate_skill` tool (per the `using-superpowers` skill body).
- Gemini CLI loads skill metadata at session start; full content activates on demand.
- The shell tool is `run_shell_command`; file edits are `replace` (in-place) or `write_file` (full file).

## Cross-runner invariants

These hold regardless of runner:

- Worktree-per-agent default
- Gitignore pre-flight for project-local worktrees
- Worktree-local venv for Python projects
- Baseline capture (test count + failing-test names + HEAD SHA + lint state)
- Commit-only, no-push discipline
- Session-log write before return

The five-pillar discipline transfers verbatim. Tool names change.

## Adapting the agent-prompt template

When adapting for a non-Cascade runner:

1. Replace `run_command` references with the runner's shell tool name.
2. Drop the `Cwd` parameter discussion if the runner does not support it; add a `cd` prefix to every command instead.
3. Replace `read_file` and `edit` with the runner-specific equivalents.
4. Adjust safe-terminal references; the Cascade-specific iron laws may not all apply, but the general principle (one logical command per line, no heredocs, no multi-line `-m`) holds.
5. Test with one dispatched agent before scaling to a parallel batch.
