# Skills Implementation

![Last Updated](https://img.shields.io/badge/Last_Updated-Sep_03%2C_2026-white?style=flat&labelColor=555)

<table width="100%">
<tr>
<td><a href="../">← Back to Claude Code Best Practice</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

<a href="#time-svg-creator-skill"><img src="../!/tags/implemented-hd.svg" alt="Implemented"></a>

Two skills are implemented in this repo as part of the **Command → Agent → Skill** architecture pattern, demonstrating two distinct skill invocation patterns: **agent skills** (preloaded) and **skills** (invoked directly).

---

## Time SVG Creator (Skill)

**File**: [`agent-teams/.claude/skills/time-svg-creator/SKILL.md`](../agent-teams/.claude/skills/time-svg-creator/SKILL.md)

```yaml
---
name: time-svg-creator
description: Creates an SVG time card showing the current time for Dubai.
  Writes the SVG to agent-teams/output/dubai-time.svg and updates
  agent-teams/output/output.md.
---

# Time SVG Creator Skill

## Task
Create an SVG time card displaying the current Dubai time, and write it
along with a summary to output files.

## Instructions
You will receive `time`, `timezone` and `formatted` from the calling context.

### 1. Create SVG Time Card
### 2. Write SVG File          -> agent-teams/output/dubai-time.svg
### 3. Write Output Summary    -> agent-teams/output/output.md

...
```

This is a **skill** — invoked directly by the command via the Skill tool. It receives the time data from the conversation context and creates the SVG card and output summary. It also ships `examples.md` and `reference.md` alongside `SKILL.md`, the progressive-disclosure pattern: the body stays short and the detail loads only when needed.

---

## Time Fetcher (Agent Skill)

**File**: [`agent-teams/.claude/skills/time-fetcher/SKILL.md`](../agent-teams/.claude/skills/time-fetcher/SKILL.md)

```yaml
---
name: time-fetcher
description: Instructions for fetching current Dubai time via bash command
user-invocable: false
---

## Dubai Time Fetcher

### Command
TZ='Asia/Dubai' date '+%Y-%m-%d %H:%M:%S %Z'

### Expected Output Format
`YYYY-MM-DD HH:MM:SS +04` (Gulf Standard Time)

### Return Format
- time: Just the time portion (HH:MM:SS)
- timezone: "GST (UTC+4)"
- formatted: The full output string from the command
```

This is an **agent skill** — preloaded into the `time-agent` at startup via the `skills:` frontmatter field. It is not invoked directly; it is domain knowledge injected into the agent's context. Note `user-invocable: false`, which hides it from the `/` menu.

---

## Two Skill Patterns

| Pattern | Invocation | Example | Key Difference |
|---------|-----------|---------|----------------|
| **Skill** | `Skill(skill: "name")` | `time-svg-creator` | Invoked directly via Skill tool |
| **Agent Skill** | Preloaded via `skills:` field | `time-fetcher` | Injected into agent context at startup |

A preloaded skill is only real if it is discoverable. Skills are found at exactly `.claude/skills/<name>/SKILL.md` — one extra directory level makes the skill invisible, with no error, and an agent preloading it runs without the knowledge it is built on. Verify by listing, never by reading the config; see [AGENTS.md](../AGENTS.md).

---

## ![How to Use](../!/tags/how-to-use.svg)

These skills live in the nested `agent-teams/` workspace, so run Claude from there:

```bash
$ cd agent-teams
$ claude
> /time-svg-creator
```

---

## ![How to Implement](../!/tags/how-to-implement.svg)

Ask Claude to create one for you — it will generate the markdown file with YAML frontmatter and body in `.claude/skills/my-skill/SKILL.md`

```markdown
---
name: my-skill
description: What the skill does and when Claude should reach for it
---

# My Skill

Instructions for what the skill does.
```
