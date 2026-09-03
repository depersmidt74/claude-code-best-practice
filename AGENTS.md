# AGENTS.md

Telegraph style. Root owns hard policy and routing; the docs own detail.
Edit this file — `CLAUDE.md` is a symlink to it.

## Start

- This repo is a reference implementation of Claude Code patterns: skills,
  subagents, commands, hooks. It is not an application.
- Best-practice question → search this repo first (`best-practice/`, `reports/`,
  `tips/`, `implementation/`, `README.md`). It is the authoritative source here;
  external docs and web search are the fallback, not the start.
- Field-level reference lives in the docs, never in this file:
  `best-practice/claude-subagents.md` (16 subagent fields),
  `claude-skills.md` (20 skill fields), `claude-commands.md`,
  `claude-settings.md` (618 setting rows). Duplicating a field list here creates
  two truths that drift; route instead.
- Scoped rules load lazily by path: `.claude/rules/*.md` with `paths:`
  frontmatter apply only when a matching file is touched. Without frontmatter a
  rule loads into every session, like this file — spend that budget carefully.

## Verification

Every rule here was written after it broke in this repository. Each cites the
incident.

**Configuration is verified by observation, not by reading.** Claude Code
reports neither an unrecognized frontmatter key nor a `SKILL.md` in the wrong
place. There is no error — the behaviour simply never happens.

| Claim | Check |
|---|---|
| A skill is installed | `claude -p "List the exact names of every skill available to you via the Skill tool, one per line. Do not call any tool."` — anything absent is not model-invocable. Not the same as absent: a skill with `disable-model-invocation: true` never appears yet runs fine as `/<name>`, so check the file for that field before calling a skill missing |
| An agent's tools are restricted | Run it with a prompt needing the forbidden tool; it reports the tools it holds |
| A hook fires | Trigger its event and look for the effect, not for the config entry |
| Any grant is actually in effect | `projects["<repo>"].hasTrustDialogAccepted` is `true` in `~/.claude.json`. On an untrusted workspace `.claude/settings.json` is ignored wholesale — Claude Code says so on stderr — and the resulting approval prompts look exactly like a working allowlist |

- `allowedTools:` in subagent frontmatter restricts nothing. Eleven agents held
  the full toolset while claiming otherwise; `weather-agent` documented a
  fail-closed guardrail it did not have. `tools:` / `disallowedTools:` are the
  fields that work. Fixed in `c67c83c`.
- A command-scoped pattern in `tools:` / `disallowedTools:` is not a subagent
  guardrail. `tools: Bash(git log:*)` left `curl` and `whoami` running;
  `disallowedTools: Bash(curl:*)` removed the whole Bash tool rather than curl.
  Subagent grants are whole-tool; command scope belongs in `permissions` in
  `.claude/settings.json`. Probes and results in
  `best-practice/claude-subagents.md`. Same false guarantee as `allowedTools:`,
  found while porting the pattern in from n8n — where it lives in a skill's
  `allowed-tools`, which widens rather than restricts.
- Unparseable frontmatter does not fail a skill. Eight probes in a clean
  workspace: a `SKILL.md` with no frontmatter, with no `name`, with no
  `description`, with invented fields, and with frontmatter that is not valid
  YAML all loaded anyway — name falling back to the directory, description to
  the body's first line, and every field written in the block silently
  discarded. The skill runs while its whole configuration is gone. Placement is
  the only breakage Claude Code enforces. Probe table in
  `best-practice/claude-skills.md`; run the frontmatter parse check under
  Commands before trusting any field.
- Skills are discovered at exactly `.claude/skills/<name>/SKILL.md`. One extra
  directory level makes a skill invisible; three had been dead for an unknown
  time, and the agent preloading them ran without the knowledge it is built on.
  Fixed in `2fea0ca`.

**Never silence the error you will need.** `curl -s` hides curl's own failures
along with its progress meter; the blocked request then reaches the next stage
as empty input and the diagnosis lands on the wrong layer. A failure here was
attributed to a network proxy when it was `curl: (3) bad range specification` —
curl reading `symbols=["A","B"]` as URL-range syntax, never opening a
connection. Visible only after `-sS` (`75f6508`), fixed with `-g` (`70861d1`).
Use `-sS`, add `-g` for bracketed URLs, and do not reach for `--fail`: it
discards the response body, which is often the only useful message.

**A skipped check is not a passed check.** Report it as skipped, name the
reason, and say in the summary that the chain is unconfirmed —
`scripts/test-fmt24h.sh` is the shape. The same holds in prose: name which paths
were exercised and which were not. "Verified" with an unexercised half is a
false claim.

**Run it before documenting it.** Both curl defects above survived reading and
died on first execution. So did the self-test's own first draft, which asserted
one symbol against a fixture containing another.

**Claims about a dependency come from its source** — the vendored file, the
upstream repository, the response on the wire. Not memory, not a wrapper. Where
the source is unreachable, say so and mark the claim unverified rather than
softening it.

## Change discipline

- Say what was verified and what was not, every time. A finding needs the
  observation that produced it, not a plausible mechanism.
- Correct a wrong diagnosis explicitly when a later observation overturns it.
  Two diagnoses in this repository's history were wrong and were corrected in
  the commit that found the real cause; silently moving on would have left the
  wrong explanation as the record.
- Touch what the task needs. A defect found in passing gets fixed in the same
  change when it is small and bounded, or named as a follow-up — never silently
  passed.
- Vendored third-party trees are imported verbatim and pinned
  (`skills-lock.json`); do not hand-edit them. Their mirrors under `.agents/`
  are gitignored.

## Map

```
.claude/agents/<name>.md              subagents
.claude/skills/<name>/SKILL.md        skills — exactly this depth
.claude/commands/<name>.md            slash commands (nested dirs namespace them)
.claude/rules/*.md                    scoped rules; paths: makes them lazy
.claude/hooks/                        hook scripts, config, sounds
.claude/settings.json                 team settings (committed)
.claude/settings.local.json           personal (gitignored)
scripts/                              runnable helpers and their self-tests
best-practice/ implementation/ reports/ tips/ changelog/   docs, see markdown-docs rule
```

Subagents **cannot** invoke other subagents through bash. Use the Agent tool:
`Agent(subagent_type="name", description="...", prompt="...")`. Avoid verbs like
"launch" in a subagent's body — they read as shell commands.

## Commands

- Skills visible in this repo: `claude -p "List the exact names of every skill
  available to you via the Skill tool, one per line. Do not call any tool."`
- Frontmatter parses: `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" <file>`
- Chain self-test: `bash scripts/test-fmt24h.sh` — network checks report SKIP
  where egress is closed, and the summary says the chain is unconfirmed.
- Hooks off for a session: `"disableAllHooks": true` in
  `.claude/settings.local.json`.

## Before cloning anything

Check what the maintainer already has, in this order, and only then clone:

1. `list_repos` with the name as query — returns their repositories **including
   forks**, which is the case the other checks miss.
2. The session's attached-repository list. It is fixed at session start, so a
   fork attached in an earlier session does not appear in it.
3. Disk: an attached repo sits at `/home/user/<repo>`, an anonymous clone at
   `/home/user/<owner>/<repo>`.

**Their fork outranks upstream.** It may carry their own commits, and it clones
with full history where an anonymous `--depth 1` clone does not.

Written after cloning `obra/superpowers` at `--depth 1` while
`depersmidt74/superpowers` already existed. The trees turned out identical, so
nothing was lost from the reading — but the history was, and the history is
where a skill's evolution and its commit-message evidence live. One `list_repos`
call would have settled it.

## Git

- One commit per file. A file gets a message about that file's change.
  Exception: a vendored import commits per imported unit, not per file — 128
  mechanical commits serve nobody.
- The commit message carries the evidence: what was observed, not what was
  intended.

## Docs

`.claude/rules/markdown-docs.md` owns documentation standards and placement.
Adding a concept or report also updates the matching table in `README.md`.
Presentation work routes per-presentation via `.claude/rules/presentation.md` —
never edit presentation HTML directly.
