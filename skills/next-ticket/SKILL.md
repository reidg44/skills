---
name: next-ticket
description: Pick the next unblocked agent-ready ticket (lowest number whose blockers are all closed) and take it end to end - read the ticket, build it test-first, verify it like a user would, commit, and close it so the next ticket unblocks. Works with GitHub issues or local markdown tickets. Also works a wayfinder map (issue labelled `wayfinder:map`) by claiming and resolving its next frontier decision ticket. Use when the user says "next ticket", "pick up the next issue", "work the backlog", "grab the next ready-for-agent issue", "next wayfinder ticket", or names an issue or map number to work.
---

# Next ticket

Pick up the next ticket and get it done. This works best in a fresh session. Each ticket
should say everything needed to build it, so don't count on context from earlier sessions.

The issue tracker is the only state. Closing a ticket is what unblocks the next one.
Tickets come in two formats:

- **Build tickets** carry the label (or `Status:` line) that marks them ready for an agent
  (default `ready-for-agent`) and list their blockers in a `## Blocked by` section, a
  `Blocked by:` line, GitHub's native issue dependencies, or a mix. Follow steps 1-5.
- **Wayfinder tickets** are children of a **map** labelled `wayfinder:map`. Each carries a
  type (`research`, `prototype`, `grilling`, `task`) and poses a question to decide, not a
  slice to build. Follow [Wayfinder maps](#wayfinder-maps) instead.

This skill works best alongside the `mattpocock-skills` plugin (github.com/mattpocock/skills).
Its `to-tickets` and `triage` skills write build tickets, and its `wayfinder` skill writes
maps. Its `tdd`, `code-review`, `grilling`, `domain-modeling`, `prototype`, and `research`
skills cover the steps below. Without it, follow the steps as written.

## 0. Find the tracker and choose the format

**Tracker.** If `docs/agents/issue-tracker.md` exists, it is the source of truth for every
tracker operation below (list, read, claim, comment, close, blockers, frontier). Use its
commands in place of the `gh` examples here. If `docs/agents/triage-labels.md` exists, take
the ready label from its `ready-for-agent` row. Without these files, assume GitHub and use the
`gh` commands as written. For a local-markdown tracker, tickets are files under
`.scratch/<feature>/issues/NN-<slug>.md`, ready ones carry the ready label on their `Status:`
line, and comments append under `## Comments`.

**Format.**

- The user named a map, or a ticket that belongs to one: use the wayfinder flow.
- The user named any other ticket: use steps 1-5.
- Otherwise check both: ready build tickets (step 1) and open maps
  (`gh issue list --state open --label wayfinder:map --json number,title`, or `map.md`
  files under `.scratch/`). If only one kind exists, use it. If both exist, take the build
  ticket, and name the map's next frontier ticket in your opening message so the user can
  redirect. Ask which to work only when the user mentioned the map, or when there is no
  unblocked build ticket and more than one open map.

**Asking the user.** Put every question to the user through the **question tool**:
`AskUserQuestion` in Claude Code, or your tool's equivalent, falling back to plain text only
when there is none. Put your recommended option first, marked `(Recommended)`. This covers
grilling and prototype tickets too, and overrides the `grilling` skill's text format for
rounds. The tool takes up to 4 questions per call, so split a bigger round into several
calls.

## 1. Pick the ticket

If the user named a ticket, use that one and skip the blocker check. Otherwise list the
candidates:

```bash
gh issue list --state open --label ready-for-agent --limit 200 --json number,title,body \
  --jq 'sort_by(.number) | .[] | {number, title, body}'
```

For each candidate, lowest number first, skip it if it has an assignee (another session has
claimed it) or also carries `ready-for-human`. Then check its blockers in both places:

- **Native dependencies**: list the open ones with
  `gh api repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by --jq '[.[] | select(.state == "open") | .number]'`.
- **Body**: the `## Blocked by` section, or a `Blocked by: #<n>, #<n>` line near the top.
  Check each listed issue with `gh issue view <n> --json state`. "None" or a missing section
  counts as unblocked. A blocker in another repo (`owner/repo#n`) needs `--repo`.

Pick the first candidate whose blockers are all **closed**. STATUS.md or the newest ticket
comment may name a different next ticket. Decide it yourself where you can:

- It names a ticket in this repo that is ready and unblocked: take that one, and say why in
  your opening message.
- It names a ticket in another repo: keep this repo's pick and mention the pointer.
- It names a ticket that is blocked or not ready, or a dependency the blocker lists lack:
  say so and ask which to take before starting.

No unblocked candidate: stop. Report each open candidate and what blocks it. Don't start a
blocked ticket. End with one next action, asked with the question tool: if open tickets are
stubs, untriaged, or waiting on a decision, offer to run `backlog-grooming` now; if the lowest
open ticket is `ready-for-human`, offer to walk it with the user, doing the agent-safe steps
yourself and handing over the rest as exact commands.

Read the full ticket with its comments:
`gh issue view <n> --json title,body,comments --jq '.title, .body, (.comments[] | "\(.author.login): \(.body)")'`.
(`--comments` alone prints no body when output is piped.) If a comment holds an
`## Agent Brief`, the newest one is the contract: it overrides the body where they disagree.
Earlier comments may also record partial progress from a previous session.

**Before any other work, tell the user what you're starting on.** Give the ticket number and
title, why it was picked (for example, lowest unblocked), and two or three sentences in plain
language on what the ticket does: the change it makes and what it touches. Mention any
partial progress from earlier comments. Then keep going without waiting for a reply.

**Keep the user oriented while you work.** Each progress line says where you are in this
skill's fixed steps (1 pick, 2 build, 3 wrap-up, 4 land, 5 report) and what just happened, for
example "Step 2 of 5 (build): 3 of 4 acceptance criteria have passing tests." The count is
always "of 5"; sub-progress goes after the colon. If your tool has a task or todo list, keep one item
per step there, with one in progress at a time. Report a failure as cause and fix ("Test
fails at `auth.spec.ts:42`: expected 200, got 401. Cause: missing auth header. Fixing."),
with no alarm words.

Then read every doc and spec the ticket points to, plus the project's agent instructions
(AGENTS.md/CLAUDE.md), STATUS.md, and `GLOSSARY.md` and ADRs in the area, where they exist.
Note the current commit (`git rev-parse HEAD`) as the ticket's **starting point** for review.

**Preflight credentials.** Before building, check every credential the verify and land steps
need: cloud CLI sessions (for example `aws sts get-caller-identity --profile <p>`), the
secrets manager being unlocked, commit signing, and dev-database access. Name anything expired
in your opening message, with the exact command that fixes it, so the user can fix it while
you build instead of finding out at the end.

## 2. Build it

- Work test-first where there's a clean seam: write a failing test, then just enough code to
  pass it, one slice at a time. If a `tdd` skill is available, use it. Take the seams under
  test from the ticket's acceptance criteria and key interfaces, and don't stop to confirm
  them with the user unless the ticket leaves them genuinely unclear. Run typechecking and
  single test files often while you work.
- Stay inside the ticket's scope. If you find related work, note it for the closing comment
  or a new ticket. Don't build it now.
- At the end, run the project's **full** test suite, lint, and typecheck. Find the commands in
  AGENTS.md/CLAUDE.md, the justfile/Makefile, or package scripts. Fix every failure, including
  failures that look unrelated, or name them explicitly in the report.
- **Check every user-facing change the way a user would.** Drive web UI in a real browser,
  call the live API, or run the actual CLI workflow. Passing tests alone don't count as done.
- Review the diff against the ticket's acceptance criteria. If a `code-review` skill is
  available, use it, and give it the starting point from step 1 as the fixed point and the
  ticket as the spec so it doesn't have to ask. Fix what the review finds, including any
  refactoring it suggests.

## 3. Wrap up the session

Always run the `wrap-session` skill once the build is verified, or once you stop early, and
**before** committing, so its doc, check, and STATUS.md edits land in the ticket's commit
instead of leaking into the next one. If it isn't available, do its steps yourself: delete
session debris, record what was learned in the right place, and update STATUS.md. Skip its
"flag uncommitted work" step and its closing summary: step 4 commits, and the report covers
the rest. If the wrap-up adds a check, run it before committing.

**Write STATUS.md as it will read once the ticket has landed.** It goes into the ticket's
commit, so anything it says about landing is out of date minutes later. Point it at the next
ticket. Leave out commit SHAs, PR numbers, and whether the work is pushed, merged, deployed,
or migrated, and leave out checks still waiting on the user. That state belongs in the ticket
comment. Done right, STATUS.md needs no second edit after step 4.

## 4. Land it

- Make one commit on the current branch with the ticket's work and the wrap-up's edits,
  with a message that references the ticket (`#<n>`). Run the commit yourself. If the user
  said they're stepping away, stage everything and note "ready to commit" in STATUS.md
  instead.
- If a signed commit fails (the user wasn't there to approve the prompt), keep everything
  staged, save the message to `.git/COMMIT_MSG_DRAFT`, and end the turn with a question-tool
  prompt to retry; on yes, run `git commit -F .git/COMMIT_MSG_DRAFT`. Every commit stays
  signed: a failed signature means stop and ask, whatever a project doc calls a fallback.
- Then ask once, with the question tool, how far to land it, for example "Push <sha>, open
  the PR, and merge when CI is green?". A yes covers every step it names: do them all, quote
  that approval when merging, watch the deploy if pushing deploys, and check the live health
  endpoint after. After a merge, delete the branch (`gh pr merge --delete-branch`).
- **"Merge when CI is green" means you wait and you merge.** Watch the checks yourself with
  one background command (`gh pr checks <n> --watch`), then merge in the same turn when they
  pass. Don't use `gh pr merge --auto`: it merges at once on a repo with no required checks.
  Don't end the turn asking the user to say "merge" again. Hand the merge back only if the
  checks fail or the wait is denied, and say which.
- The landing approval also covers follow-up commits that only touch docs or STATUS.md (for
  example a correction after the close). Commit and push them the same way without asking
  again. Never end the session with a commit the user approved landing but that isn't pushed.
- Some steps only the user can run: production migrations, infrastructure applies, anything
  the permission system has denied this session, anything that needs their credentials.
  Chain them into as few commands as possible and end the turn with them, one per code block,
  each ready to run as-is from the right directory. Don't close the ticket until every
  acceptance criterion that depends on them has actually passed.
- When all acceptance criteria are met, close the ticket with a comment that says what
  shipped, the commit SHA, and anything deferred:
  `gh issue close <n> --comment "<summary>"`.
- If the session ends before the work is finished, comment on the ticket with what's done
  and what's left, and leave it open. The ticket holds the progress. STATUS.md, if you touch
  it, only points at the ticket. Don't commit unfinished work unless the user asks.

## 5. Report

Give one short summary. No preamble and no closing pleasantries. Open with what now works
and how to try it ("Magic-link login works: run `just dev` and open `/login`"), then:

- which ticket you worked
- what changed
- verification evidence: test/lint results and what you checked by hand
- commands the user still needs to run
- which ticket is now unblocked next
- **Wrap-up:** always the last line, so the user sees it without scrolling. Say that
  `wrap-session` ran and what it did: files cleaned, docs or checks touched, and where
  STATUS.md points. For example: "Wrap-up: ran wrap-session. Removed 2 scratch scripts,
  added a gotcha to AGENTS.md, STATUS.md points at #42." If it didn't run, say so and why.

If the `i-have-adhd` skill is active, its rules take precedence over this progress and report
shape.

## Wayfinder maps

A wayfinder map plans a large effort as a chain of decisions. The `wayfinder` skill owns the
map's format and rules. If you can read that skill, follow it. This section is the short
version for working the map, one ticket at a time.

Tickets resolve **decisions**, not deliverables, unless the map's `## Notes` say the effort
carries execution into the map. Resolve **one** ticket per session, except research tickets,
which can be resolved in parallel. Other sessions may be working the same map, so re-read
state right before every write. In anything the user reads, refer to the map and its tickets
by title, not bare number.

### Pick the ticket

1. Read the map body only (`gh issue view <map> --json title,body`, or `map.md`). Note its
   `## Destination` and `## Notes`. Don't load every ticket body.
2. If the user named a ticket, use it. Otherwise run the tracker doc's **frontier query**.
   Without a tracker doc, list the map's children in map order:
   `gh api repos/{owner}/{repo}/issues/<map>/sub_issues --paginate --jq '.[] | {number, title, state, assignees: [.assignees[].login], labels: [.labels[].name]}'`
   (or the task list in the map body), and keep the ones that are open, unassigned, and
   unblocked (check blockers as in step 1). Take the first in map order, not the lowest
   number.
3. **Claim it** before any other work (`gh issue edit <n> --add-assignee @me`, or
   `Status: claimed` locally).
4. No frontier ticket: stop. Report each open child by title and what blocks or claims it.
   If no open children remain and `## Not yet specified` is empty, the way is clear: tell
   the user the map is done and that the next step is a spec (`to-spec`), not more tickets.

Read the full ticket with its comments (the `--json` command from step 1). Fetch related or
closed tickets only when you need their detail.

Before resolving it, tell the user what you're starting on: the ticket's title and type, and
two or three plain sentences on the question it poses and what deciding it will unlock. Then
keep going without waiting for a reply (grilling and prototype tickets need the user anyway).

### Resolve it by type

Read the type from the ticket's `wayfinder:<type>` label or `Type:` line. The body doesn't
state it.

- **research** (agent alone): investigate the question against primary sources. If a
  `research` skill is available, run it in a subagent and keep its findings on a pushed
  `research/<name>` branch that is never merged. Link the findings from the ticket.
- **task** (agent alone where possible): do the manual work the ticket names. If it needs
  the user (accounts, credentials, access), give them an exact checklist and wait. Record
  what was done and any facts later tickets need.
- **grilling** (with the user): question the user until the decision is made. If `grilling`
  and `domain-modeling` skills are available, use both. Never answer your own questions on
  the user's behalf. If the user isn't present, release the claim and stop.
- **prototype** (with the user): build a cheap, rough artifact to react to (use a
  `prototype` skill if available), link it from the ticket, and decide with the user.
- Also use any skills the map's `## Notes` name.

Only write production code if the map's `## Notes` say the effort includes execution. In that
case, use step 2's build rules for that part of the work.

### Record it

1. Post the answer as a comment (`gh issue comment <n> --body "<answer>"`, or an `## Answer`
   section locally). Include the decision, the reasons, and links to any assets.
2. Close the ticket (`gh issue close <n>`, or `Status: resolved`).
3. Re-read the map body, then append one line under `## Decisions so far`:
   `- [<ticket title>](<ticket url>): <one-line gist>`. Don't restate the full answer.
4. Update the map for what the answer revealed:
   - Turn fog under `## Not yet specified` that is now sharp enough into new child tickets.
     Create them and link them to the map, then add blocking edges in a second pass, once
     every ticket has a real number. Remove each graduated patch from `## Not yet specified`.
   - Close any ticket that now sits past the destination and note it under `## Out of scope`.
   - Update or close any ticket the decision has made wrong.
5. Wrap up the session as in [step 3](#3-wrap-up-the-session), then commit any repo changes
   (the wrap-up's edits, plus code or findings files if the ticket produced them) in one
   commit, following step 4's commit rules.
6. Report: which ticket you resolved (by title), the decision, what changed on the map, and
   the next frontier ticket by title. End with the **Wrap-up** line, as in
   [step 5](#5-report).

If the session ends before the decision is made, comment with the progress so far, release
the claim (`gh issue edit <n> --remove-assignee @me`, or clear `Status: claimed`), and leave
the ticket open. Then wrap up and report the same way.
