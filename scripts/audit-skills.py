#!/usr/bin/env python3
"""Audit skill trees: placement, frontmatter, and fields that silently do nothing.

    python3 scripts/audit-skills.py .claude/skills [more/skills ...]

Defaults to .claude/skills when given no arguments. Exit code 0 when nothing is
broken, 1 when at least one ERROR is reported.

Why this exists. Claude Code never rejects a skill. Eight probes in a clean
workspace proved it: no frontmatter, no `name`, no `description`, invented
fields, and frontmatter that is not valid YAML all loaded anyway — the block
discarded, name falling back to the directory, description to the body's first
line, and every field written in that block gone. The skill runs while its whole
configuration is missing, with no error and no warning. Placement is the only
breakage the harness enforces. See best-practice/claude-skills.md.

So the checks below are the only way those defects surface at all:

  ERROR   SKILL.md not at <root>/<name>/SKILL.md     -> the skill is invisible
  ERROR   frontmatter absent, unclosed, or not YAML  -> every field is dropped
  ERROR   a dead field alias (allowedTools, tools …) -> reads as a guardrail,
                                                        enforces nothing
  ERROR   description + when_to_use over 1536 chars  -> truncated
  WARN    name does not match the directory          -> fine for a plugin skill,
                                                        which namespaces as
                                                        plugin:name
  WARN    a field outside the documented set         -> silently ignored
  WARN    no description                             -> the body's first line
                                                        becomes the trigger text

The field list mirrors the table in best-practice/claude-skills.md. Update both
together or they drift.
"""

import os
import sys

import yaml

VALID = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools",
    "disallowed-tools", "model", "effort", "context", "agent", "background",
    "hooks", "paths", "shell", "metadata", "license", "compatibility",
}

# Fields that look like they work and do not. Each maps to the one that does.
DEAD = {
    "allowedTools": "allowed-tools",
    "disallowedTools": "disallowed-tools",
    "allowed_tools": "allowed-tools",
    "disallowed_tools": "disallowed-tools",
    "tools": "allowed-tools — skills have no tools: field, that is a subagent field",
    "whenToUse": "when_to_use",
    "argumentHint": "argument-hint",
    "userInvocable": "user-invocable",
    "disableModelInvocation": "disable-model-invocation",
}

CAP = 1536


def audit(root):
    """Yield (level, skill, message) for one skill root."""
    if not os.path.isdir(root):
        yield "ERROR", root, "not a directory"
        return

    # A SKILL.md deeper than one level is the one defect the harness enforces,
    # by never loading the skill. Report it against the directory that owns it.
    for dirpath, _, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if "SKILL.md" in files and rel != "." and os.sep in rel:
            owner = rel.split(os.sep)[0]
            yield "ERROR", os.path.join(root, owner), (
                f"SKILL.md one level too deep at {rel}/SKILL.md — "
                "the skill is invisible, with no error"
            )

    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue
        skill = os.path.join(root, name)
        sp = os.path.join(path, "SKILL.md")
        if not os.path.isfile(sp):
            continue  # the deep-placement walk above already reported it

        text = open(sp, encoding="utf-8", errors="replace").read()

        if not text.startswith("---"):
            yield "ERROR", skill, "no frontmatter — name and description come from the body"
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            yield "ERROR", skill, "frontmatter not closed by a second ---"
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            yield "ERROR", skill, (
                f"frontmatter is not valid YAML ({str(e).splitlines()[0]}) — "
                "the whole block is discarded and the skill still loads"
            )
            continue
        if fm is None:
            yield "ERROR", skill, "frontmatter is empty"
            continue
        if not isinstance(fm, dict):
            yield "ERROR", skill, f"frontmatter is a {type(fm).__name__}, not a mapping"
            continue

        for key in fm:
            if key in DEAD:
                yield "ERROR", skill, f"'{key}' does nothing — use '{DEAD[key]}'"
            elif key not in VALID:
                yield "WARN", skill, f"'{key}' is outside the documented set and is ignored"

        if "name" in fm and str(fm["name"]) != name:
            yield "WARN", skill, (
                f"name '{fm['name']}' differs from the directory — expected for a "
                "plugin skill, which namespaces as plugin:name"
            )
        if "description" not in fm:
            yield "WARN", skill, "no description — the body's first line becomes the trigger text"
        else:
            n = len(str(fm["description"])) + len(str(fm.get("when_to_use", "")))
            if n > CAP:
                yield "ERROR", skill, f"description + when_to_use is {n} chars, over the {CAP} cap"


def main():
    roots = sys.argv[1:] or [os.path.join(".claude", "skills")]
    findings = [f for root in roots for f in audit(root)]

    errors = [f for f in findings if f[0] == "ERROR"]
    for level, skill, msg in findings:
        print(f"{level:<5} {skill}: {msg}")

    counted = sum(
        1
        for root in roots
        if os.path.isdir(root)
        for d in os.listdir(root)
        if os.path.isfile(os.path.join(root, d, "SKILL.md"))
    )
    print(f"\n{counted} skills checked in {len(roots)} root(s): "
          f"{len(errors)} errors, {len(findings) - len(errors)} warnings")
    if not findings:
        print("Nothing broken. Note this proves the frontmatter parses and the "
              "fields are real — not that any field has the effect it claims. "
              "That still takes a run.")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
