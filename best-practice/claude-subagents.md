# Sub-agents Best Practice

![Last Updated](https://img.shields.io/badge/Last_Updated-Sep%2001%2C%202026%2011%3A38%20AM%20PKT-white?style=flat&labelColor=555) ![Version](https://img.shields.io/badge/Claude_Code-v2.1.252-blue?style=flat&labelColor=555)<br>
[![Implemented](https://img.shields.io/badge/Implemented-2ea44f?style=flat)](../implementation/claude-subagents-implementation.md)

Claude Code subagents — frontmatter fields and official built-in agent types.

<table width="100%">
<tr>
<td><a href="../">← Back to Claude Code Best Practice</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## Frontmatter Fields (16)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | string | Yes | When to invoke. Use `"PROACTIVELY"` for auto-invocation by Claude |
| `tools` | string/list | No | Comma-separated allowlist of tools (e.g., `Read, Write, Edit, Bash`). Inherits all tools if omitted. Supports `Agent(agent_type)` syntax to restrict spawnable subagents; the older `Task(agent_type)` alias still works. Whole-tool granularity only — see [Command-scoped patterns](#command-scoped-patterns-do-not-work-here) |
| `disallowedTools` | string/list | No | Tools to deny, removed from inherited or specified list. Whole-tool granularity only — see [Command-scoped patterns](#command-scoped-patterns-do-not-work-here) |
| `model` | string | No | Model to use: `sonnet`, `opus`, `haiku`, a full model ID (e.g., `claude-opus-4-6`), or `inherit` (default: `inherit`) |
| `permissionMode` | string | No | Permission mode: `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan` |
| `maxTurns` | integer | No | Maximum number of agentic turns before the subagent stops |
| `skills` | list | No | Skill names to preload into agent context at startup (full content injected, not just made available) |
| `mcpServers` | list | No | MCP servers for this subagent — server name strings or inline `{name: config}` objects |
| `hooks` | object | No | Lifecycle hooks scoped to this subagent. All hook events are supported; `PreToolUse`, `PostToolUse`, and `Stop` are the most common |
| `memory` | string | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | boolean | No | Set to `true` to always run as a background task (default: `false`) |
| `effort` | string | No | Effort level override when this subagent is active: `low`, `medium`, `high`, `xhigh`, `max` (Opus 4.6 only). Default: inherits from session |
| `isolation` | string | No | Set to `"worktree"` to run in a temporary git worktree (auto-cleaned if no changes) |
| `initialPrompt` | string | No | Auto-submitted as the first user turn when this agent runs as the main session agent (via `--agent` or the `agent` setting). Commands and skills are processed. Prepended to any user-provided prompt |
| `color` | string | No | Display color for the subagent in the task list and transcript: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, or `cyan` |

### Command-scoped patterns do not work here

`tools:` and `disallowedTools:` name whole tools. A command-scoped pattern such
as `Bash(git log:*)` is valid syntax in a permission rule, so it is tempting to
write one here as a guardrail — but a subagent grant is not a permission rule.
Three throwaway probe agents, run against a trusted workspace whose
`.claude/settings.json` allows `Bash(*)`:

| Frontmatter | Asked to run | Result |
|---|---|---|
| `tools: Bash(git log:*)` | `git log`, `curl --version`, `whoami` | all three ran — the pattern narrowed nothing |
| `tools: Bash, Read`<br>`disallowedTools: Bash(curl:*)` | `git log`, `curl --version` | neither ran; the agent reported holding only `Read` — the whole Bash tool was removed |
| `tools: Bash(git status:*), Bash(git log:*)` on an **untrusted** workspace | `git log`, `git push --dry-run`, `rm -f …`, `curl --version` | `git log` ran, the rest asked for approval — the untrusted default, not the pattern |

The third row is why this is easy to get wrong. On an untrusted workspace
`settings.json` is ignored wholesale, side-effecting commands fall back to an
approval prompt, and the outcome looks exactly like a working allowlist. Trust
the workspace before concluding anything about a tool grant.

So the only fail-closed lever a subagent has is naming the tool: `Read, Grep,
Glob, Bash` grants Bash entirely, and `disallowedTools: Bash` removes it
entirely. To restrict *which commands* run, use `permissions` in
`.claude/settings.json` — that is the layer that reads command scopes. Writing
one into `tools:` produces the same false guarantee as `allowedTools:` did in
`c67c83c`.

Skills differ: `allowed-tools` in `SKILL.md` does take command-scoped patterns
(`Bash(gh:*)`), but it *widens* — it lists what runs without a prompt while the
skill is active. It is prompt reduction, not a guardrail. See
[claude-skills.md](claude-skills.md).

---

## ![Official](../!/tags/official.svg) **(5)**

| # | Agent | Model | Tools | Description |
|---|-------|-------|-------|-------------|
| 1 | `general-purpose` | inherit | All | Complex multi-step tasks — the default agent type for research, code search, and autonomous work |
| 2 | `Explore` | haiku | Read-only (no Write, Edit) | Fast codebase search and exploration — optimized for finding files, searching code, and answering codebase questions |
| 3 | `Plan` | inherit | Read-only (no Write, Edit) | Pre-planning research in plan mode — explores the codebase and designs implementation approaches before writing code |
| 4 | `statusline-setup` | sonnet | Read, Edit | Configures the user's Claude Code status line setting |
| 5 | `claude-code-guide` | haiku | Glob, Grep, Read, WebFetch, WebSearch | Answers questions about Claude Code features, Agent SDK, and Claude API |

---

## Sources

- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [CLI reference — Claude Code Docs](https://code.claude.com/docs/en/cli-reference)
- [Claude Code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
