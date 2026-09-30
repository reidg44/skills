# Agent instructions for this repo

This repo is a skills-only plugin consumed by Claude Code, Codex, and Copilot CLI. See README.md.

- Skills live in `skills/<name>/SKILL.md` with `name` (equal to the dir name) and `description` frontmatter. Write skills tool-agnostically: don't assume Claude-only tools or frontmatter.
- Do NOT add `version` to `.claude-plugin/plugin.json`. Claude Code would pin to it and stop tracking commits.
- The root `plugin.json` `version` is for Copilot/Codex. Run `just bump` when shipping skill changes.
- Keep the plugin name `reidg44-skills` and marketplace name `reidg44` in sync across all four manifests.
- Run `just validate` before finishing. Hooks: prek + betterleaks.
- This repo may be public. Never write real names, personal emails, hostnames, LAN IPs, or absolute local paths (`/Users/<name>/…`), whether in files or commit messages. Use `~/…` or placeholders like `<project>/`. `scripts/check-pii.sh` enforces this, so never bypass it with `--no-verify`.
