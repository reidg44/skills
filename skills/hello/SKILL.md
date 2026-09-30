---
name: hello
description: Smoke-test skill that confirms the reidg44-skills plugin is installed and reports which agent tool loaded it. Use when the user says "hello skills", asks whether the reidg44-skills plugin is installed, or wants to check that skill sync is working.
---

# Hello

Reply with one short confirmation that includes:

1. The line `reidg44-skills plugin is loaded ✅`
2. Which agent tool you are running in (Claude Code, Codex, or GitHub Copilot CLI), if you can tell.
3. The path this SKILL.md was loaded from, if you know it. The path shows whether the skill came from a plugin install or a local symlink.
