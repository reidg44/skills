---
name: new-ticket
description: Turn a request into a new ticket on the issue tracker - size it first (quick ticket, needs grilling, or too big for one session), confirm the size with the user, grill only when the size calls for it, then show the draft and create it only after the user approves. Works with GitHub issues or local markdown tickets. Use when the user says "new ticket", "file an issue", "open a ticket for", "make a ticket", "add this to the backlog", or describes work they want tracked. Also shapes an existing needs-triage ticket in place when the user names one ("shape #12", "triage #12", "make #12 ready").
---

# New ticket

Turn what the user is asking for into a ticket that the next agent can pick up and trust.
Small, clear requests become a ticket right away. Requests with open decisions get grilled
first. Requests too big for one session go to a wayfinder map instead.

The issue tracker is visible to everyone. **Nothing is created until the user approves the
final draft.** Every path below ends at that approval.

This skill works best alongside the `mattpocock-skills` plugin (github.com/mattpocock/skills).
Its `grilling` and `domain-modeling` skills run the interview, its `to-tickets` and `to-spec`
skills shape multi-ticket work, and its `wayfinder` skill charts large efforts. If you can
read those skills, follow them where this skill points to them. Without them, follow the
steps as written.

## Asking the user

Put every question to the user through the **question tool**: `AskUserQuestion` in Claude
Code, or your tool's equivalent. Fall back to plain text only when there is none. This
covers the size check, every grilling round, and the final approval, and it overrides the
`grilling` skill's text format for rounds.

- Put your recommended option first and mark it `(Recommended)`. Keep any context to a line
  or two in the question or option descriptions.
- The tool takes up to 4 questions per call and 2-4 options per question, and the user can
  always type their own answer. If a grilling round has more than 4 questions, ask them in
  several calls, one after another, within the same round.
- When the user needs to see something long first (a draft ticket, a breakdown), show it as
  text, then ask the question with the tool.
- A question that only has a free-text answer (a fact only the user knows) can stay in
  plain text.

## 1. Find the tracker

If `docs/agents/issue-tracker.md` exists, use its commands for every tracker operation. If
`docs/agents/triage-labels.md` exists, take label names from it. Without these files, assume
GitHub and use `gh`. For a local-markdown tracker, tickets are files under
`.scratch/<feature>/issues/NN-<slug>.md`, with the state label on a `Status:` line.

## 2. Gather the facts

Facts are your job, never the user's. Before sizing:

- Read the project's agent instructions (AGENTS.md/CLAUDE.md), and `GLOSSARY.md` and ADRs
  in the area, where they exist. Use the glossary's terms in the ticket.
- Look at the code the request touches: is it already built, where would the change land,
  and how many modules does it cross?
- Search open and recently closed tickets for a duplicate or a close neighbor
  (`gh issue list --state all --search "<keywords>" --limit 20`). If one exists, tell the
  user and offer to comment on or update it instead of creating a new one.

**Shaping an existing ticket.** If the request names an open ticket that hasn't been shaped
(labelled `needs-triage`, or with no state label), for example one captured by `new-idea`,
shape that ticket in place. Don't create a second one. Read its body and comments as the
request, then follow steps 3-5 as usual. In step 5 show the draft as the ticket's new title
and body. In step 6, edit instead of create.

## 3. Size it

Put the request in one of three sizes:

- **Quick.** One clear change. You can write testable acceptance criteria now without
  asking the user anything, and one fresh agent session can build it. Typical: a bug with
  clear steps to reproduce, a small tweak, a rename, a config change.
- **Needs grilling.** Decisions only the user can make are still open: behavior, UX, data
  shape, scope, or edge cases. Or the request reads more than one way, crosses several
  modules, or will likely split into more than one ticket.
- **Wayfinder.** Too big for one session to plan, let alone build. The destination itself is
  foggy, or deciding it needs research or prototypes first.

When it's between two sizes, pick the larger one. A short grilling costs less than a ticket
that sends an agent the wrong way.

For **Needs grilling**, also estimate the rounds. List the open decisions the ticket depends
on, and group them by which ones need another's answer first. Each layer of that chain is
one round. Most tickets need one or two rounds. If you count more than three, the request
is probably several tickets or a wayfinder map: say so, and propose a smaller first ticket
or the larger size.

**Confirm the size with the user before going further.** Give the size, two or three
reasons tied to what you found in step 2, the estimated rounds for Needs grilling (with
the open decisions behind the estimate), and the path that comes next. Let them override
it, for example "just make it quick". Ask with the question tool, with your size as the
recommended option. Wait for the answer.

## 4. Shape it by size

### Quick

Draft one ticket using the template in [Ticket template](#ticket-template). Go to step 5.

### Needs grilling

Grill the request into shape with the `grilling` and `domain-modeling` skills, one round of
questions at a time. Never answer your own questions for the user.

Keep the grilling **lean**, within the rounds you estimated:

- Ask only decisions the ticket depends on: ones that change what gets built or its
  acceptance criteria. Decisions the building agent can make on its own (naming, internal
  structure, choice of library) stay out of the grilling. Mention them in the ticket only if
  they need a constraint.
- Ask every question whose prerequisites are settled in the same round, through the
  question tool, with your recommended answer as the first option of each, so the user can
  accept most of them in one pass.
- Look up facts in the code and docs yourself, before the round, instead of asking.
- Move nice-to-have scope to the ticket's `## Out of scope` section instead of grilling it.

Grilling is done when nothing is left that the acceptance criteria depend on, not when every
branch of the idea has been explored. If you reach your estimate and decisions are still
open, tell the user how many are left and why, and ask with the question tool: one more round, draft
now with your recommended answers marked as assumptions in the ticket, or move up to
Wayfinder.

Then look at what came out:

- **One ticket's worth:** draft it using the [Ticket template](#ticket-template).
- **Several slices:** break it into tracer-bullet vertical slices, following `to-tickets`
  if you can read it. Each slice is demoable on its own, fits one fresh session, and lists
  the slices that block it. If the work needs a spec as the parent (many user stories, or
  decisions every slice shares), draft it following `to-spec`, and make the slices its
  sub-issues.

Go to step 5.

### Wayfinder

Don't write tickets. Write one or two lines naming the destination: what reaching the end
of the effort looks like. Then tell the user to run the `wayfinder` skill with that
destination, which charts the map with them. Stop here.

## 5. Get approval

Show the user the full draft exactly as it will be created: title, body, labels, and
blocking edges for each ticket. For several tickets, show them as a numbered list in
dependency order, and the parent spec if there is one.

Then ask with the question tool: approve (recommended), edit, or cancel. Apply any edits and show the changed draft again. Repeat until the user
approves or cancels. **Create nothing until they approve.**

## 6. Create it

- Label each ticket `ready-for-agent` (or the name `docs/agents/triage-labels.md` maps it
  to) plus a category label (`bug` or `enhancement`). The user approved the draft, so it
  skips triage and `next-ticket` can pick it up right away. Use `ready-for-human` instead
  when the work needs a person: credentials, design calls, or manual testing.
- **One ticket:** `gh issue create --title "<title>" --body-file <file> --label ready-for-agent --label <category>`.
- **Several tickets:** create the parent spec first, if there is one. Then create the slices
  in dependency order, blockers first. Add blocking edges in a second pass, once every
  ticket has a real number. Use native dependencies where the tracker has them:
  `gh api --method POST repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by -F issue_id=<blocker-db-id>`,
  where the database id comes from `gh api repos/{owner}/{repo}/issues/<blocker> --jq .id`.
  Otherwise fill in each ticket's `## Blocked by` section.
- **Local tracker:** write one file per ticket, numbered after the highest existing ticket in
  that feature folder, with `Status: ready-for-agent`.
- **Shaping an existing ticket:** re-read it first, since another session may have changed
  it. Replace the title and body, remove the untriaged label, and add the ready and category
  labels:
  `gh issue edit <n> --title "<title>" --body-file <file> --remove-label needs-triage --add-label ready-for-agent --add-label <category>`.
  Add a short comment saying the ticket was shaped and what was decided. Keep the original
  idea's wording in the comment if the new body drops it. For a local tracker, rewrite the
  file and its `Status:` line. If shaping split it into several tickets, keep the original
  as the first slice or the parent, and create the rest as above.

## 7. Report

Give the link (or path) and title of each ticket created or shaped, its labels and blockers, and the
next step: run `next-ticket` to build it.

## Ticket template

Describe behavior and interfaces, not file paths or line numbers, which go stale. Every
acceptance criterion must be checkable on its own.

```markdown
## What to build

The end-to-end behavior this ticket makes work, from the user's point of view. For a bug,
what happens now, what should happen, and the steps to reproduce.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Out of scope

- Nearby work this ticket should not touch

## Blocked by

- Each blocking ticket, or "None (can start immediately)". Leave this section out when
  blockers are set as native dependencies.
```

For a slice that belongs to a parent spec, add a `## Parent` section at the top that links
the parent.
