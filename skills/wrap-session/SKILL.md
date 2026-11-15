---
name: wrap-session
description: End-of-session ritual - clean up debug files, route what was learned into the right place (checks, AGENTS.md/CLAUDE.md, glossary/ADRs, docs), write STATUS.md for the next session, and flag uncommitted work. Use when the user says "wrap up", "pause", "document the current status", "I need to step away", "update the docs", or is about to exit mid-task. To resume a project, use reorient.
---

# Wrap up the session

Ending a session usually means some combination of "clean up the debug files", "update the documentation with what you learned", and "document status so a future agent can pick this up". Do all of it as one ritual.

If the user says what the next session will focus on, tailor STATUS.md to that.

## Steps, in order

1. **Clean up session debris.** Delete any debug scripts, scratch files, one-off test files, or downloaded assets created this session that aren't part of the project. If unsure whether a file is debris, list it and ask.

2. **Route what was learned.** For each thing discovered this session that a future session would need, pick the one place where it does the most good. Prefer the earlier options:
   - **A mistake a tool could catch** (a banned API, a wrong import, a file in the wrong place, a forgotten step): propose a deterministic check, such as a lint rule, hook, test, or `just` recipe, instead of writing a rule for agents to remember. Add it if it's small. Otherwise list it in the summary.
   - **A judgment call reviewers should enforce**: `CODING_STANDARDS.md`, if the project has one.
   - **A new domain term, or a hard-to-reverse decision**: `GLOSSARY.md` or an ADR under `docs/adr/`, if the project keeps them. If a `domain-modeling` skill is available, use it. Don't create these files just for this.
   - **A gotcha, command, or pointer every session needs**: the agent instructions file, `AGENTS.md`, or `CLAUDE.md` if that's what the project uses (if `CLAUDE.md` just imports `@AGENTS.md`, edit `AGENTS.md`). This loads into every session, so keep entries terse, and prefer a one-line pointer to a doc over the detail itself. If a `writing-for-agents` skill is available, follow it.
   - **Changed setup or usage**: `README.md`, or the project's runbooks and docs.

   If running in Claude Code and the change is substantial, `/claude-md-management:revise-claude-md` handles the agent instructions file well. Otherwise edit directly.

3. **Write STATUS.md:** what remains with concrete next steps, blockers/decisions needed, and exact commands to resume.
   - **Rewrite, don't append.** STATUS.md describes the project now. It is not a log. Delete entries for finished work and closed tickets: the tracker and `git log` keep that history. Keep the whole file to about 60 lines.
   - **Nothing a command can check.** Leave out commit SHAs, PR numbers, CI results, login state, and whether work is pushed, merged, deployed, or migrated. That state changes minutes later and makes the file wrong. If one of those is the next action, write it under Resume here as a command to run, not as a status claim. Write only what is true now, never a predicted PR number or SHA. When a skill that lands the work runs this wrap, write STATUS.md as it will read once the work has landed.
   - **Resume here, at the top.** Open with a `## Resume here` section of at most 5 lines: the one next action, the exact first command for it, and where it sits in the plan ("step 3 of 5") if a plan is in flight. A reader who stops after this section should still know how to start.
   - **Link, don't restate.** Point at issues, commits, specs, plans, and ADRs by URL or path instead of copying them in. If the session worked a tracked issue, put the progress on the issue as a comment and keep STATUS.md to a pointer to it. The tracker holds that state.
   - **Suggested skills:** name the skills the next session should start with (for example `next-ticket`, `tdd`, `diagnosing-bugs`).
   - **No secrets.** Leave out API keys, passwords, tokens, and personal data. Refer to `.env` variable names instead.

4. **Flag uncommitted work, and offer to commit the wrap's own edits.** When another skill runs this wrap as part of its own flow and commits afterwards (for example `next-ticket`), skip this step and leave committing to that skill. Otherwise:
   - **The session's real work:** flag it, do not commit it. Report it in the chat summary, not in STATUS.md: git state changes as soon as the user commits, and the next session can run `git status`. The one exception: if the user said they're stepping away and real work is uncommitted, add one line to STATUS.md saying it's ready to commit.
   - **Files this wrap created or edited** (STATUS.md, doc updates from step 2): don't leave them uncommitted without a word. Ask once, with the question tool (`AskUserQuestion` in Claude Code, or your tool's equivalent, plain text only if there is none): "Commit and push the wrap-up edits?", with yes as the first option, marked `(Recommended)`. Say in the question if a push starts a deploy. On yes, make one docs commit with only those files and push it. If the session's branch is already merged, make the edits and the commit on the default branch, not on the merged branch or its worktree. If the user said they're stepping away, skip the question and name the files in the summary.

5. **One-line summary** back to the user. Start with what now works, if the session shipped anything. Then list docs touched, checks proposed or added, and files cleaned, and end with where STATUS.md points next. No closing pleasantries.

If the `i-have-adhd` skill is active, its rules take precedence over this summary shape.
