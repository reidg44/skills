---
name: reorient
description: Re-enter a dormant or stalled project - reconstruct where things stand from STATUS.md, the issue tracker, and git, check that record against the repo, then propose one concrete next step. Read-only. Use when the user asks "what's the status", "where did we leave off", "what's next", or returns to a project after time away. The counterpart to wrap-session.
---

# Reorient on a project

The user is coming back to a project after days or weeks. Within one response they should know where things stand and what to do next, without re-explaining the project. This is the entry-side counterpart to `wrap-session`.

## Steps

1. **Read the record, newest first:**
   - `STATUS.md`, if present. This is the intended handoff, including its suggested skills.
   - The agent instructions file (`AGENTS.md` or `CLAUDE.md`) for project state and gotchas.
   - `git log --oneline -15` and `git status`. Uncommitted work is often the real "where we left off".
   - Any plans, specs, or issues STATUS.md links to.
   - The issue tracker, if the project uses one (see `docs/agents/issue-tracker.md` if it exists): open tickets that are claimed or have recent progress comments, ready tickets whose blockers are all closed, and any open `wayfinder:map`.

2. **Check the record against reality.** STATUS.md may be stale. Do the commands it mentions still exist? Is the branch it names still checked out? Are the tickets it points at still open? If the repo contradicts the status doc, say so explicitly. Don't silently trust either.

3. **Report in this shape.** Lead with the action and skip preamble.
   - **Recommended next step, first line:** one concrete action, not a menu, with a time estimate in real units ("about 20 minutes", "one session"). Then a starter the user can do in under two minutes, usually one exact command. If it's the next unblocked ticket, name it and suggest `next-ticket`.
   - One sentence: what this project is and its end goal.
   - What's done (working, verified), stated as what now works.
   - What's in flight (uncommitted changes, half-finished features, claimed tickets, open bugs).
   - Show at most 5 items per list, most relevant first, and say how many more there are. Mention a second problem only after the main report, as its own line.
   - Questions only where you're genuinely blocked on the user's input. Ask after reviewing, not instead of reviewing. Ask questions with discrete choices through the question tool (`AskUserQuestion` in Claude Code, or your tool's equivalent; plain text only if there is none), with the recommended option first.

4. **Wait for direction before changing anything.** Reorientation is read-only.

If the `i-have-adhd` skill is active, its rules take precedence over this report shape.
