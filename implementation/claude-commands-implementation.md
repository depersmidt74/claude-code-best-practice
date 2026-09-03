# Commands Implementation

![Last Updated](https://img.shields.io/badge/Last_Updated-Sep_03%2C_2026-white?style=flat&labelColor=555)

<table width="100%">
<tr>
<td><a href="../">← Back to Claude Code Best Practice</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

<a href="#time-orchestrator"><img src="../!/tags/implemented-hd.svg" alt="Implemented"></a>

The time orchestrator command is implemented in this repo as the entry point of the **Command → Agent → Skill** architecture pattern, demonstrating how commands orchestrate multi-step workflows.

---

## Time Orchestrator

**File**: [`agent-teams/.claude/commands/time-orchestrator.md`](../agent-teams/.claude/commands/time-orchestrator.md)

```yaml
---
description: Fetch the current time for Dubai (GST, UTC+4) and create a visual SVG time card
model: haiku
---

# Time Orchestrator Command

## Workflow

### Step 1: Fetch Current Dubai Time
Use the Agent tool to invoke the time agent:
- subagent_type: time-agent
- prompt: Fetch the current time for Dubai (Asia/Dubai, UTC+4). Return exactly
  three fields: `time`, `timezone`, `formatted`...

### Data Contract
The time-agent MUST return these three fields:
- time · timezone · formatted

### Step 2: Create SVG Time Card
Use the Skill tool to invoke the time-svg-creator skill:
- skill: time-svg-creator
- args: Pass the time data from Step 1

...
```

The command orchestrates the whole workflow: it invokes the `time-agent` via the Agent tool, waits for the agent's three fields, then invokes the `time-svg-creator` skill via the Skill tool.

Two details are worth copying into your own commands:

- **A named data contract.** The command states exactly which three fields the agent must return, so the handoff to the skill is not guesswork.
- **Explicit tool routing.** It says outright that the agent goes through the Agent tool and the skill through the Skill tool, and that the two must run sequentially. Subagents cannot invoke other subagents through bash — see [AGENTS.md](../AGENTS.md).

---

## ![How to Use](../!/tags/how-to-use.svg)

The command lives in the nested `agent-teams/` workspace, so run Claude from there:

```bash
$ cd agent-teams
$ claude
> /time-orchestrator
```

---

## ![How to Implement](../!/tags/how-to-implement.svg)

Ask Claude to create one for you — it will generate the markdown file with YAML frontmatter and body in `.claude/commands/<name>.md`

---

<a href="claude-agent-teams-implementation.md"><img src="../!/tags/orchestration-workflow-hd.svg" alt="Orchestration Workflow"></a>

The time orchestrator is the **Command** in the Command → Agent → Skill orchestration pattern. It is the entry point — it delegates data fetching to the `time-agent` and invokes the standalone `time-svg-creator` skill for visual output.

| Component | Role | This Repo |
|-----------|------|-----------|
| **Command** | Entry point, user interaction | [`/time-orchestrator`](../agent-teams/.claude/commands/time-orchestrator.md) |
| **Agent** | Fetches data with preloaded skill (agent skill) | [`time-agent`](../agent-teams/.claude/agents/time-agent.md) with [`time-fetcher`](../agent-teams/.claude/skills/time-fetcher/SKILL.md) |
| **Skill** | Creates output independently (skill) | [`time-svg-creator`](../agent-teams/.claude/skills/time-svg-creator/SKILL.md) |
