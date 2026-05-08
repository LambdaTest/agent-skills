#!/usr/bin/env bash
# This file finds the SKILL.md files in the directories and subdirectories in which it is located,
# and installs each skill into ~/.claude/skills/<name>/
#
# Usage:
#   ./testmu-skill-installer.sh           # scans current directory
#   ./testmu-skill-installer.sh /path/to  # scans given directory

set -euo pipefail

SKILLS_DIR="$HOME/.claude/skills"
SOURCE_DIR="${1:-.}"
INSTALLED=0
SKIPPED=0
ERRORS=0

# ── Create ~/.claude/skills if it doesn't exist ──────────────────────────────
if [ ! -d "$HOME/.claude" ]; then
  mkdir -p "$SKILLS_DIR"
  echo "Created ~/.claude/skills (first-time setup)"
elif [ ! -d "$SKILLS_DIR" ]; then
  mkdir -p "$SKILLS_DIR"
  echo "Created ~/.claude/skills"
fi

echo ""
echo "Scanning for skills in: $(realpath "$SOURCE_DIR")"
echo "Installing into:        $SKILLS_DIR"
echo ""

# ── Helper Function: The function extracts 'name' value from SKILL.md frontmatter ───────────────────
# extract_name() {
#   local file="$1"
#   # Match:  name: my-skill-name  (with or without quotes, ignores leading spaces)
#   local name
#   name=$(sed -n '/^---/,/^---/p' "$file" \
#          | grep -E '^\s*name\s*:' \
#          | head -1 \
#          | sed -E 's/^\s*name\s*:\s*//;s/^\s+//;s/\s+$//;s/^["'"'"']//;s/["'"'"']$//')
#   echo "$name"
# }

extract_name() {
  local file="$1"
  awk '/^---/{f++} f==1 && /^name:/{gsub(/^name:[[:space:]]*|[[:space:]]*$/, ""); print; exit}' "$file"
}


# ── Find and install every SKILL.md ──────────────────────────────────────────
while IFS= read -r skill_md; do

  skill_name=$(extract_name "$skill_md")

  # Guard: no name found in frontmatter
  if [ -z "$skill_name" ]; then
    echo "  Skipping $skill_md  (no 'name' field found in frontmatter)"
    ((ERRORS++)) || true
    continue
  fi

  skill_folder="$(dirname "$skill_md")"
  target="$SKILLS_DIR/$skill_name"

  # Guard: source is already the target
  if [ "$(realpath "$skill_folder")" = "$(realpath "$target" 2>/dev/null || echo __none__)" ]; then
    echo "Skipping '$skill_name'  (source and target are the same location)"
    ((SKIPPED++)) || true
    continue
  fi

  # Install: copy entire skill folder contents into target
  mkdir -p "$target"
  cp -r "$skill_folder/." "$target/"

  echo " Installed: '$skill_name'  →  $target"
  ((INSTALLED++)) || true

done < <(find "$(realpath "$SOURCE_DIR")" -name "SKILL.md" -not -path "$(realpath "$SKILLS_DIR")/*")

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
if [ "$INSTALLED" -eq 0 ] && [ "$SKIPPED" -eq 0 ] && [ "$ERRORS" -eq 0 ]; then
  echo "No SKILL.md files found. Please check the location in which this file needs to be present."
else
  echo "Process Completed!  Installed: $INSTALLED  |  Skipped: $SKIPPED  |  Errors: $ERRORS"
  [ "$INSTALLED" -gt 0 ] && echo "    Restart Claude Code to pick up the new skills."
  [ "$ERRORS"    -gt 0 ] && echo "    Fix the skipped files by adding a 'name:' field to their frontmatter."
fi
echo ""