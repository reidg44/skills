---
name: wrap-session
description: End-of-session ritual - clean up debug files, update AGENTS.md/CLAUDE.md/docs with what was learned, write STATUS.md for the next session, and flag uncommitted work. Use when the user says "wrap up", "pause", "document the current status", "I need to step away", "update the docs", or is about to exit mid-task.
---

# Wrap up the session

Ending a session usually means some combination of "clean up the debug files", "update the documentation with what you learned", and "document status so a future agent can pick this up". Do all of it as one ritual.

## Steps, in order

1. **Clean up session debris.** Delete any debug scripts, scratch files, one-off test files, or downloaded assets created this session that aren't part of the project. If unsure whether a file is debris, list it and ask.

2. **Update project docs with what was learned.** Anything discovered this session that a future session would need: new gotchas, changed procedures, fixed root causes, new hardware/config facts. Targets, in priority order:
   - The agent instructions file: `AGENTS.md`, or `CLAUDE.md` if that's what the project uses (if `CLAUDE.md` just imports `@AGENTS.md`, edit `AGENTS.md`). Covers gotchas, commands, conventions. Keep entries terse, since this loads into every session.
   - `README.md`, only if user-facing setup/usage changed
   - Project-specific runbooks/docs if they exist

   If running in Claude Code and the change is substantial, `/claude-md-management:revise-claude-md` does this well. Otherwise edit directly.

3. **Write STATUS.md:** what was completed, what remains with concrete next steps, blockers/decisions needed, and exact commands to resume.

4. **Flag uncommitted work, do not commit.** List modified/untracked files worth committing. Commits may be signed and need the user present. If they said they're stepping away, explicitly note "uncommitted changes ready for you to commit" in STATUS.md instead of attempting it.

5. **One-line summary** back to the user: docs touched, files cleaned, where STATUS.md points next.
