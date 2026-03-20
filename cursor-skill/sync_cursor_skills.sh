#!/usr/bin/env bash
#
# Sync Cursor skills from cursor-skill/<name>/ to .cursor/skills/<name>/
# Run from anywhere: ./cursor-skill/sync_cursor_skills.sh
#
# Options:
#   --link    Symlink instead of copy (edits in cursor-skill/ apply immediately)
#   --source DIR   Skill parent directory (default: this script's directory)
#   --target DIR   Destination (default: <project-root>/.cursor/skills)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$SCRIPT_DIR"
TARGET_DIR="$ROOT/.cursor/skills"
USE_LINK=0

usage() {
  echo "Usage: $0 [--link] [--source DIR] [--target DIR]" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --link) USE_LINK=1; shift ;;
    --source)
      [[ $# -ge 2 ]] || usage
      SOURCE_DIR="$(cd "$2" && pwd)"
      shift 2
      ;;
    --target)
      [[ $# -ge 2 ]] || usage
      TARGET_DIR="$(cd "$2" && pwd)"
      shift 2
      ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
synced=()

for path in "$SOURCE_DIR"/*; do
  [[ -d "$path" ]] || continue
  name="$(basename "$path")"
  [[ -f "$path/SKILL.md" ]] || continue

  dest="$TARGET_DIR/$name"
  if [[ "$USE_LINK" -eq 1 ]]; then
    rm -rf "$dest"
    ln -s "$path" "$dest"
  else
    rm -rf "$dest"
    cp -R "$path" "$dest"
  fi
  synced+=("$name")
done

if [[ ${#synced[@]} -eq 0 ]]; then
  echo "No skill directories (with SKILL.md) found in $SOURCE_DIR"
  exit 0
fi

IFS=', '
echo "Synced ${#synced[@]} skill(s) to ${TARGET_DIR#$ROOT/}: ${synced[*]}"
