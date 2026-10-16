---
name: next-ticket
description: Pick the next unblocked agent-ready GitHub issue (lowest number whose blockers are all closed) and take it end to end - read the ticket, build it test-first, verify it like a user would, commit, and close the issue so the next ticket unblocks. Also works a wayfinder map (issue labelled `wayfinder:map`) by claiming and resolving its next frontier decision ticket. Use when the user says "next ticket", "pick up the next issue", "work the backlog", "grab the next ready-for-agent issue", "next wayfinder ticket", or names an issue or map number to work.
---

# Next ticket

Pick up the next ticket and get it done. This works best in a fresh session. Each ticket
should say everything needed to build it, so don't count on context from earlier sessions.

The issue tracker is the only state. Closing a ticket is what unblocks the next one.
Tickets come in two formats:

- **Build tickets** carry a label that marks them ready for an agent (default
  `ready-for-agent`) and list their blockers in a `## Blocked by` section, in GitHub's native
  issue dependencies, or both. Follow steps 1-4.
- **Wayfinder tickets** are child issues (sub-issues) of a **map** issue labelled
  `wayfinder:map`. Each carries a `wayfinder:<type>` label (`research`, `prototype`,
  `grilling`, `task`) and poses a question to decide, not a slice to build. Follow
  [Wayfinder maps](#wayfinder-maps) instead.

This skill works best alongside the `mattpocock-skills` plugin (github.com/mattpocock/skills).
Its `to-tickets` skill writes build tickets and its `wayfinder` skill writes maps. Its `tdd`,
`code-review`, `grilling`, `domain-modeling`, `prototype`, and `research` skills cover the
steps below. Without it, follow the steps as written.

## 0. Choose the format

- The user named a map, or an issue labelled `wayfinder:*`: use the wayfinder flow.
- The user named any other issue: use steps 1-4.
- Otherwise check both: `ready-for-agent` candidates (step 1) and open maps
  (`gh issue list --state open --label wayfinder:map --json number,title`). If only one kind
  exists, use it. If both exist, or there is more than one open map, ask the user which to
  work.

## 1. Pick the ticket

If the user named an issue number, use that one and skip the blocker check. Otherwise list
the candidates:

```bash
gh issue list --state open --label ready-for-agent --limit 200 --json number,title,body \
  --jq 'sort_by(.number) | .[] | {number, title, body}'
```

If the project uses a different label (check AGENTS.md/CLAUDE.md or `gh label list`), use that.

For each candidate, lowest number first, skip it if it has an assignee (another session has
claimed it). Then check its blockers in both places:

- **Native dependencies**: list the open ones with
  `gh api repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by --jq '[.[] | select(.state == "open") | .number]'`.
- **Body**: the `## Blocked by` section, or a `Blocked by: #<n>, #<n>` line near the top.
  Check each listed issue with `gh issue view <n> --json state`. "None" or a missing section
  counts as unblocked. A blocker in another repo (`owner/repo#n`) needs `--repo`.

Pick the first candidate whose blockers are all **closed**.

- No unblocked candidate: stop. Report each open candidate and what blocks it. Don't start a
  blocked ticket.
- Otherwise, say which issue you picked and why in one line, then keep going without waiting.

Read the full ticket with `gh issue view <n> --comments`. Earlier comments may record partial
progress from a previous session. Then read every doc and spec the ticket points to, plus the
project's agent instructions (AGENTS.md/CLAUDE.md) and STATUS.md if there is one.

## 2. Build it

- Work test-first where there's a clean seam: write a failing test, make it pass, refactor.
  If a `tdd` skill is available, use it. Run typechecking and single test files often while
  you work.
- Stay inside the ticket's scope. If you find related work, note it for the closing comment
  or a new issue. Don't build it now.
- At the end, run the project's **full** test suite, lint, and typecheck. Find the commands in
  AGENTS.md/CLAUDE.md, the justfile/Makefile, or package scripts. Fix every failure, including
  failures that look unrelated, or name them explicitly in the report.
- **Check every user-facing change the way a user would.** Drive web UI in a real browser,
  call the live API, or run the actual CLI workflow. Passing tests alone don't count as done.
- Review the diff against the ticket's acceptance criteria. If a `code-review` skill is
  available, use it. Fix what the review finds.

## 3. Land it

- Commit to the current branch with a message that references the issue (`#<n>`). If the user
  said they're stepping away, or commits need them present (for example, signed commits),
  don't commit. Stage the work and note "ready to commit" in STATUS.md.
- Some steps only the user can run: database migrations against production, deploys,
  infrastructure applies, anything that needs their credentials. List these at the end as
  exact commands. Don't close the issue until every acceptance criterion that depends on
  them has actually passed.
- When all acceptance criteria are met, close the issue with a comment that says what
  shipped, the commit SHA, and anything deferred:
  `gh issue close <n> --comment "<summary>"`.
- If the session ends before the work is finished, comment on the issue with what's done and
  what's left, and update STATUS.md. Leave the issue open.

## 4. Report

Give one short summary:

- which issue you worked
- what changed
- verification evidence: test/lint results and what you checked by hand
- commands the user still needs to run
- which ticket is now unblocked next

## Wayfinder maps

A wayfinder map plans a large effort as a chain of decisions. Its tickets resolve
**decisions**, not deliverables, unless the map's `## Notes` say the effort carries execution
into the map. Resolve **one** ticket per session. Other sessions may be working the same map,
so re-read state right before every write.

### Pick the ticket

1. Read the map body only: `gh issue view <map> --json title,body`. Note its
   `## Destination` and `## Notes`. Don't load every ticket body.
2. If the user named a ticket, use it. Otherwise list the map's children **in map order**:
   `gh api repos/{owner}/{repo}/issues/<map>/sub_issues --paginate --jq '.[] | {number, title, state, assignees: [.assignees[].login], labels: [.labels[].name]}'`.
   Where sub-issues aren't enabled, the children are the task list in the map body, in that
   order.
3. The **frontier** is the children that are open, unassigned, and unblocked. Check blockers
   the same way as step 1 (native dependencies first, then a `Blocked by:` line). Take the
   first frontier ticket in map order, not the lowest number.
4. **Claim it** before any other work: `gh issue edit <n> --add-assignee @me`. Then say which
   ticket you picked, by its title, in one line.
5. No frontier ticket: stop. Report each open child by title and what blocks or claims it.
   If no open children remain, the map may be done. Say so and point at its
   `## Not yet specified` section.

Read the full ticket with `gh issue view <n> --comments`. Fetch related or closed tickets
only when you need their detail.

### Resolve it by type

- **research** (agent alone): investigate the question against primary sources. If a
  `research` skill is available, use it. Link any findings file from the ticket.
- **task** (agent alone where possible): do the manual work the ticket names. If it needs
  the user (accounts, credentials, access), give them an exact checklist and wait.
- **grilling** (with the user): question the user until the decision is made. If `grilling`
  and `domain-modeling` skills are available, use both. Never answer your own questions on
  the user's behalf. If the user isn't present, unassign the ticket and stop.
- **prototype** (with the user): build a cheap, rough artifact to react to (use a
  `prototype` skill if available), link it from the ticket, and decide with the user.
- Also use any skills the map's `## Notes` name.

Only write production code if the map's `## Notes` say the effort includes execution. In that
case, use step 2's build rules for that part of the work.

### Record it

1. Post the answer as a comment: `gh issue comment <n> --body "<answer>"`. Include the
   decision, the reasons, and links to any assets.
2. Close the ticket: `gh issue close <n>`.
3. Re-read the map body, then append one line under `## Decisions so far`:
   `- [<ticket title>](<ticket url>): <one-line gist>`. Don't restate the full answer.
4. Update the map for what the answer revealed:
   - Turn fog under `## Not yet specified` that is now sharp enough into new child tickets.
     Create them, link them as sub-issues, then add blocking edges in a second pass. Remove
     each graduated patch from `## Not yet specified`.
   - Close any ticket that now sits past the destination and note it under `## Out of scope`.
   - Update or close any ticket the decision has made wrong.
5. Report: which ticket you resolved (by title), the decision, what changed on the map, and
   the next frontier ticket by title.

If the session ends before the decision is made, comment with the progress so far, unassign
yourself (`gh issue edit <n> --remove-assignee @me`), and leave the ticket open.
