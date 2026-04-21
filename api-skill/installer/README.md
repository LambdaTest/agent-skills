# Skill Installer for Claude Code

A shell script that recursively discovers and installs all your custom Claude Code skills in one command.

## Requirements

- macOS or Linux
- Claude Code installed (`npm install -g @anthropic-ai/claude-code`)
- Bash 3.2+

## Installation

Download `testmu-skill-installer_code.sh` and make it executable:

```bash
chmod +x testmu-skill-installer_code.sh
```

The file is intentionally kept non-executable.

## Usage

Run the script from anywhere, passing your skills folder as the argument:

```bash
bash testmu-skill-installer_code.sh /path/to/your/skills
```

Or from the same folder as the script:

```bash
bash testmu-skill-installer_code.sh ~/Documents/Skills
```

## What It Does

- Recursively scans the given folder for every `SKILL.md` file at any depth
- Reads the `name` field from each skill's YAML frontmatter
- Copies each skill folder into `~/.claude/skills/<skill-name>/`
- Creates `~/.claude/skills/` automatically if it doesn't exist
- Skips skills with missing `name` fields and reports them

## Skill Structure

Each skill must be a folder containing a `SKILL.md` file with valid YAML frontmatter:

```
Skills/
├── my-skill/
│   └── SKILL.md        ← must have name: field
├── nested/
│   └── another-skill/
│       └── SKILL.md    ← any depth works
└── SKILL.md            ← root level also supported
```

Each `SKILL.md` must start with a frontmatter block:

```yaml
---
name: my-skill-name
description: >
  Describe when Claude should use this skill.
---

# Skill instructions go here
```

**If the frontmatter block is absent, the skill will be ignored for installation.**

## After Installation

Restart Claude Code for the new skills to be picked up:

```bash
/exit   # inside Claude Code
claude  # relaunch
```

Or verify skills are installed:

```bash
find ~/.claude/skills/ -name "SKILL.md"
```

## Notes

- This installer is for **Claude Code only**. It does not support Claude Desktop or Claude.ai.
- Skills are installed globally to `~/.claude/skills/` and are available across all your projects.
- Re-running the script is safe — existing skills will be overwritten with the latest version.
- Skills with a missing or empty `name:` field in their frontmatter will be skipped and reported as errors.

## Uninstalling a Skill

To remove a specific skill:

```bash
rm -rf ~/.claude/skills/<skill-name>
```

To remove all installed skills:

```bash
rm -rf ~/.claude/skills/
```
