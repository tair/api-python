# Claude skills (project install)

This directory mirrors [`cursor-skills/`](../cursor-skills/): each immediate subfolder that contains a `SKILL.md` file is an [Agent Skill](https://code.claude.com/docs/en/skills). Sync them into Claude Code’s project skills location with the script below.

## Install into Claude Code

From the **repository root**:

```bash
chmod +x claude-skills/sync_claude_skills.sh   # once
./claude-skills/sync_claude_skills.sh
```

This copies (or, with `--link`, symlinks) each skill into `.claude/skills/<skill-name>/`, which Claude Code loads for this project.

### Options

- **`--link`** — Symlink instead of copy so edits under `claude-skills/` apply without re-running sync.
- **`--source DIR`** — Sync from another folder (e.g. `./claude-skills/sync_claude_skills.sh --source "$PWD/cursor-skills"` to install Cursor-authored skills into `.claude/skills/`).
- **`--target DIR`** — Override destination (default: `<repo>/.claude/skills`).

### User-wide skills

To install for all projects, copy or symlink the same skill folders into `~/.claude/skills/` (Claude Code user skills directory). This repo’s script targets **project-local** `.claude/skills/` by default.

## Relationship to `cursor-skills/`

- **`cursor-skills/`** → `.cursor/skills/` (Cursor)
- **`claude-skills/`** → `.claude/skills/` (Claude Code)

Skill content can be duplicated here or kept only under `cursor-skills/` and synced with `--source cursor-skills`.
