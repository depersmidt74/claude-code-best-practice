# Sub-agents Implementation

![Last Updated](https://img.shields.io/badge/Last_Updated-Sep_03%2C_2026-white?style=flat&labelColor=555)

<table width="100%">
<tr>
<td><a href="../">← Back to Claude Code Best Practice</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

<a href="#time-agent"><img src="../!/tags/implemented-hd.svg" alt="Implemented"></a>

The time agent is implemented in this repo as an example of the **Command → Agent → Skill** architecture pattern, demonstrating two distinct skill patterns.

---

## Time Agent

**File**: [`agent-teams/.claude/agents/time-agent.md`](../agent-teams/.claude/agents/time-agent.md)

```yaml
---
name: time-agent
description: Use this agent to fetch the current time for Dubai, UAE
  (Asia/Dubai timezone, UTC+4). This agent fetches real-time Dubai time
  using its preloaded time-fetcher skill.
tools: Bash
model: haiku
color: blue
maxTurns: 3
skills:
  - time-fetcher
---

You are the time-agent. Your job is to fetch the current Dubai time.

## Instructions

1. Use the Bash tool to run: `TZ='Asia/Dubai' date '+%Y-%m-%d %H:%M:%S %Z'`
2. Parse the output and return three fields: `time`, `timezone`, `formatted`
3. Return these values clearly so the calling command can extract them

Do NOT invoke any other agents or skills.
```

The agent has one preloaded skill (`time-fetcher`) that carries the command and the output format. It returns the three fields to the calling command.

Three things this file gets right, each of which broke somewhere in this repo before:

- **`tools:`, not `allowedTools:`.** `allowedTools:` in subagent frontmatter restricts nothing — eleven agents here held the full toolset while claiming otherwise, fixed in `c67c83c`.
- **Whole-tool grants.** `tools: Bash` grants Bash entirely. A command-scoped pattern such as `Bash(date:*)` would narrow nothing here; command scope belongs in `permissions` in `.claude/settings.json`. See [claude-subagents.md](../best-practice/claude-subagents.md).
- **A tight `maxTurns`.** Three turns is enough for one command and a parse, and it caps a runaway.

---

## ![How to Use](../!/tags/how-to-use.svg)

The agent lives in the nested `agent-teams/` workspace, so run Claude from there:

```bash
$ cd agent-teams
$ claude
> what time is it in dubai?
```

---

## ![How to Implement](../!/tags/how-to-implement.svg)

You can create an agent using the `/agents` command,

```bash
$ claude
> /agents
```

or ask Claude to create one for you — it will generate the markdown file with YAML frontmatter and body in `.claude/agents/<name>.md`

Whatever you write in the frontmatter, confirm it by observation: run the agent with a prompt that needs a forbidden tool and see what it actually holds. Claude Code reports neither an unrecognized field nor a grant that does not apply.

---

<a href="claude-agent-teams-implementation.md"><img src="../!/tags/orchestration-workflow-hd.svg" alt="Orchestration Workflow"></a>

The time agent is the **Agent** in the Command → Agent → Skill orchestration pattern. It receives the workflow from the `/time-orchestrator` command and fetches the time using its preloaded skill (`time-fetcher`). The command then invokes the standalone `time-svg-creator` skill to create the visual output.

| Component | Role | This Repo |
|-----------|------|-----------|
| **Command** | Entry point, user interaction | [`/time-orchestrator`](../agent-teams/.claude/commands/time-orchestrator.md) |
| **Agent** | Fetches data with preloaded skill (agent skill) | [`time-agent`](../agent-teams/.claude/agents/time-agent.md) with [`time-fetcher`](../agent-teams/.claude/skills/time-fetcher/SKILL.md) |
| **Skill** | Creates output independently (skill) | [`time-svg-creator`](../agent-teams/.claude/skills/time-svg-creator/SKILL.md) |
