# reidg44-skills

Personal [Agent Skills](https://agentskills.io) packaged as **one plugin** that installs into
Claude Code, OpenAI Codex CLI, and GitHub Copilot CLI. Edit a skill here, push, and each
tool picks up the change (after the one-time auto-update setup below).

## Layout

```
skills/<name>/SKILL.md             # the skills (shared by all three tools)
plugin.json                        # Agent Plugins manifest: Codex + Copilot (has "version")
.claude-plugin/plugin.json         # Claude Code manifest (no "version", so it tracks git SHA)
.claude-plugin/marketplace.json    # marketplace for Claude Code + Copilot
.agents/plugins/marketplace.json   # marketplace for Codex
justfile                           # new / validate / bump / try
scripts/check-pii.sh               # privacy guard hook (see below)
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

## Install with `npx skills` (any agent)

The [`skills` CLI](https://github.com/vercel-labs/skills) installs individual skills into
Claude Code, Codex, Copilot, Cursor, OpenCode, and many other agents. It copies skills into
the agent's skills folder instead of installing the plugin, so skills get plain names
(`plain-language`, not `/reidg44-skills:plain-language`) and don't update on their own.

```sh
npx skills add reidg44/skills --list                                # see what's available
npx skills add reidg44/skills --skill plain-language -a claude-code # one skill, this project
npx skills add reidg44/skills --skill '*' -a claude-code -g         # all skills, user-wide
npx skills update                                                   # pull the latest versions
```

Project installs go in the agent's folder in the current project (for example
`.claude/skills/`) and are recorded in `skills-lock.json`. Add `-g` to install for your user
instead. Use `-a '*'` to install into every agent the tool supports.

## Keep it auto-updating (one time per machine)

Claude Code and Copilot CLI don't auto-update plugins from third-party marketplaces unless
you turn it on. Codex does it by default. Do this once on each machine after installing.

**Claude Code**: auto-update is off by default for third-party marketplaces. Turn it on
either way:
- In a session, run `/plugin`, open the **Marketplaces** tab, select **reidg44**, and choose
  **Enable auto-update**.
- Or add this to `~/.claude/settings.json`:
  ```json
  {
    "extraKnownMarketplaces": {
      "reidg44": {
        "source": { "source": "github", "repo": "reidg44/skills" },
        "autoUpdate": true
      }
    }
  }
  ```

About 10 minutes after your first message in a session, Claude Code checks for new commits
(it tracks the git SHA, since `.claude-plugin/plugin.json` has no `version`). Run
`/reload-plugins` to use the new version, or start a new session. If you set
`DISABLE_AUTOUPDATER=1`, `DISABLE_UPDATES=1`, or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`,
plugin auto-update is off too unless you also set `FORCE_AUTOUPDATE_PLUGINS=1`.
To update by hand: `claude plugin update reidg44-skills@reidg44`.

**GitHub Copilot CLI**: auto-update is off by default for third-party marketplaces. Add this
to `~/.copilot/settings.json` (not `config.json`, which Copilot ignores for settings):
```json
{
  "extraKnownMarketplaces": {
    "reidg44": {
      "source": { "source": "github", "repo": "reidg44/skills" },
      "autoUpdate": true
    }
  }
}
```
Plugins then update at the start of each interactive or `-p` session. Copilot ignores
`autoUpdate` set in a repository's settings, and it skips auto-update in CI by default.
It isn't documented whether Copilot detects updates by `version` or by commit, so
run `just bump` before pushing. To update by hand: `copilot plugin update --all`.

**OpenAI Codex CLI**: on by default. Each time Codex starts, it runs `git ls-remote` on every
Git marketplace and reinstalls the plugin when the commit SHA changes. There's no setting to
switch this off short of disabling plugins (`[features] plugins = false`). New skills show up
in your next session. To update by hand: `codex plugin marketplace upgrade reidg44`.

**`npx skills`**: never auto-updates. Run `npx skills update` (add `-g` for user-wide installs).

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
  addresses (except GitHub/Anthropic noreply and `example.com`/`example.org`), and private LAN IPs.
- **Personal, never committed:** create a gitignored `.pii-denylist` with one fixed string per
  line (real name, macOS username, computer name, personal email). Each machine needs its own.

Write paths as `~/…` or `<project>/…`. For a deliberate false positive, put `pii-allow` on that
line. Commits must use a `users.noreply.github.com` email.
