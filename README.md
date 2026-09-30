# reidg44-skills

Personal [Agent Skills](https://agentskills.io) packaged as **one plugin** that installs into
Claude Code, OpenAI Codex CLI, and GitHub Copilot CLI. Edit a skill here, push, and each
tool picks up the change.

## Layout

```
skills/<name>/SKILL.md             # the skills (shared by all three tools)
plugin.json                        # Agent Plugins manifest: Codex + Copilot (has "version")
.claude-plugin/plugin.json         # Claude Code manifest (no "version", so it tracks git SHA)
.claude-plugin/marketplace.json    # marketplace for Claude Code + Copilot
.agents/plugins/marketplace.json   # marketplace for Codex
```

## Install (one time per machine)

**Claude Code**
```sh
claude plugin marketplace add reidg44/skills
claude plugin install reidg44-skills@reidg44
```
Skills show up namespaced, e.g. `/reidg44-skills:plain-language`.

**GitHub Copilot CLI**
```sh
copilot plugin marketplace add reidg44/skills
copilot plugin install reidg44-skills@reidg44
```

**OpenAI Codex CLI**
```sh
codex plugin marketplace add reidg44/skills
```
Then in a Codex session run `/plugins`, toggle **reidg44-skills** on, and start a new session.

## How updates flow

| Tool | Detects updates by | What you do |
|------|--------------------|-------------|
| Claude Code | git commit SHA | Nothing. It auto-updates at startup (or run `claude plugin marketplace update reidg44`). |
| Codex | git commit SHA (`git ls-remote` at startup) | Nothing. Or run `codex plugin marketplace upgrade`. |
| Copilot CLI | not documented, so assume `version` | Run `just bump` before pushing, then `copilot plugin update --all`. |

To have Copilot auto-update too, set `autoUpdate: true` on this marketplace's entry
under `extraKnownMarketplaces` in Copilot's settings.

## Authoring workflow

```sh
just new my-skill "Does X. Use when Y."   # scaffold
$EDITOR skills/my-skill/SKILL.md
just try "prompt that should trigger it"  # run Claude Code against this checkout, no install needed
just validate                             # also runs as a prek hook on commit
just bump                                 # patch-bump plugin.json version (for Copilot)
git commit && git push
```

Every `SKILL.md` needs `name` (matching its directory) and `description` frontmatter. Codex
requires both.

## Privacy guard

This repo may be public, so a prek hook (`scripts/check-pii.sh`) blocks identifying info in
file contents and commit messages, and requires a noreply commit email. (The commit author
*name* is not checked.)

- **Generic, committed:** absolute home paths (`/Users/…`, `/home/…`, `C:\Users\…`), email
  addresses other than GitHub noreply, and private LAN IPs.
- **Personal, never committed:** create a gitignored `.pii-denylist` with one fixed string per
  line (real name, macOS username, computer name, personal email). Each machine needs its own.

Write paths as `~/…` or `<project>/…`. For a deliberate false positive, put `pii-allow` on that
line. Commits must use a `users.noreply.github.com` email.
