---
name: backlog-grooming
description: Review every open ticket in the backlog against the code as it is today - is it still needed, does it need updating, is it split right, and is the order (blocking edges) still correct - then propose one grouped plan and apply it after the user approves. Also offers to triage the untriaged tickets, shaping the ones the user picks into ready tickets. Works with GitHub issues or local markdown tickets. Use when the user says "groom the backlog", "clean up the tickets", "are these issues still relevant", "re-order the backlog", "backlog review", "triage the backlog", or before a run of next-ticket after the code has moved on.
---

# Backlog grooming

Tickets are written against the code as it was. The code moves on, and tickets go stale:
some get done by accident, some point at things that were renamed, and some are blocked by
the wrong things. Grooming brings the backlog back in line with the code so that the next
agent picking up a ticket can trust it.

The issue tracker is the only state, and changes to it are visible to everyone. **Propose
first, apply after the user approves.** Don't close, edit, re-label, or comment on anything
before that.

## 1. Find the tracker and the backlog

- If `docs/agents/issue-tracker.md` exists, use its commands for every tracker operation. If
  `docs/agents/triage-labels.md` exists, use its label names. Without them, assume GitHub and
  use `gh`.
- List every open ticket with its labels, assignees, body, and comments:
  `gh issue list --state open --limit 500 --json number,title,labels,assignees,body,comments,updatedAt`.
  For a local tracker, read every ticket file under `.scratch/*/issues/`.
- Read each ticket's blockers: native dependencies
  (`gh api repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by`), then any
  `## Blocked by` section or `Blocked by:` line.
- Read the project's agent instructions (AGENTS.md/CLAUDE.md), STATUS.md, `GLOSSARY.md`,
  and ADRs where they exist, plus `git log --oneline -50` to see what changed recently.

Sort tickets into groups and say how many are in each before starting, for example "31 open:
22 ready-for-agent, 3 ready-for-human, 4 untriaged, 1 wayfinder map with 6 children."

- **Untriaged** tickets (no state label, or `needs-triage`) haven't been shaped yet, so skip
  the update and order checks for them. Check each one for already done, duplicate, and
  obsolete (step 2, "Is it still needed?"), then assess the rest for triage (step 2, "What
  would triage take?"). Grooming offers to triage them in step 3 and does it in step 5. A
  backlog that is groomed but still untriaged gives next-ticket nothing new to pick.
- **Wayfinder** maps and their children belong to the `wayfinder` skill. Check them only for
  tickets already answered by the code or by a closed decision, and leave the map's structure
  alone.
- Everything else is groomed in step 2.

If the user named a label, milestone, or set of tickets, groom only those.

## 2. Check each ticket

For a large backlog (roughly more than 15 tickets), split the tickets into batches and check
them in parallel with sub-agents if your tool supports them. Give each one the ticket list,
the checklist below, and the finding format, and tell it not to write anything. Otherwise
check the tickets one at a time yourself.

### Is it still needed?

- **Already done.** Search the code for the behavior the ticket asks for, by concept, not
  only by its wording. Search `git log` for commits that mention the ticket number. Run a
  quick read-only check if that settles it.
- **Duplicate** of another open ticket, or **superseded** by a ticket, ADR, or decision made
  since.
- **Obsolete.** The feature, file, or service it targets was removed, or the plan it served
  was abandoned.
- **Stale claim.** It has an assignee but no activity for a long time (roughly two weeks),
  so the claim is probably abandoned and is hiding the ticket from next-ticket.

### Does it need updating?

- **Stale references.** Names, types, commands, file paths, or glossary terms that have
  changed. Prefer describing behavior and interfaces over file paths, which go stale fast.
- **Weak acceptance criteria.** Missing, vague ("works correctly"), or no longer matching
  the code around it. Each criterion should be checkable on its own.
- **Contract drift.** If a comment holds an `## Agent Brief`, check the brief, since it
  overrides the body.
- **Wrong label.** A `ready-for-agent` ticket that actually needs a human (credentials,
  design calls, manual testing) or more information from someone.
- **Wrong size.** Too big for one fresh session: propose a split into vertical slices, each
  one demoable on its own. Too small to stand alone: propose merging it into a neighbor.

### Is the order still correct?

Order comes from blocking edges. next-ticket takes the lowest-numbered ticket whose blockers
are all closed, and issue numbers can't change, so fix order only through blocking edges.

- **Missing edge.** A ticket depends on another ticket's work but doesn't list it as a
  blocker, so it could be picked up too early.
- **Unneeded edge.** A blocker the ticket doesn't really depend on, which holds it back.
- **Blocker that will never close**, because it was closed as won't-fix or is obsolete
  under the checks above. Re-point or remove the edge.
- **Cycles** in the blocking graph.
- **Priority.** If something more urgent sits behind less urgent work, propose the edge
  changes that bring it forward, and say what they push back.

### What would triage take?

For each untriaged ticket that is still needed, work out what it would take to make it
ready. Don't write to the ticket yet.

- **Quick.** The request reads one way and the code shows how to build it. Draft the shaped
  ticket now: title, body, acceptance criteria, labels, and blockers.
- **Needs answers.** List the questions only the user can answer, at most 5, most important
  first.
- **Too big** for one fresh session. Propose the split.
- **Not for an agent.** It needs a human (credentials, a design call, manual testing) or
  information from someone else. Say which, and who.

### Finding format

Each finding gives the ticket number and title, the problem, the evidence (`file:line`, a
commit SHA, or a linked ticket), the proposed change, and a confidence level (high, medium,
or low). Ask an open question instead of guessing when only the user can know, for example
whether a feature is still wanted.

## 3. Propose the plan

Check each finding yourself before it goes in the plan. Don't trust a sub-agent's finding
unchecked. Then present one plan, grouped by action:

- **Close:** already done, duplicate, superseded, or obsolete, with the evidence for each.
- **Update:** each ticket with the exact edit (new wording, new acceptance criteria, label
  change).
- **Re-order:** each blocking edge to add or remove, and the resulting next few tickets in
  the order next-ticket would pick them.
- **Split or merge:** the proposed new tickets, their titles, and their blocking edges.
- **Release claims:** stale assignees to remove.
- **Triage:** every untriaged ticket that is still needed, grouped by what triage would
  take: quick (with the drafted ticket), needs answers (with the question count), too big
  (with the split), and not for an agent (with the label it would get).
- **Flag:** open questions for the user.
- **No change:** a one-line count, so the user knows the rest were checked.

Then ask the user to approve, edit, or drop parts of the plan, along with the open questions
from **Flag**. Ask with the question tool: `AskUserQuestion` in Claude Code, or your tool's
equivalent, falling back to plain text only when there is none. Put the recommended option
first, marked `(Recommended)`. The tool takes up to 4 questions per call, so for a large
plan ask one question per action group (for example "Close these 5 tickets?"), in several
calls if needed. Wait for the answers.

Always ask the **Triage** question when any untriaged ticket is still needed. Don't leave
triage for the report. Ask which tickets to triage now, as a multi-select where the tool has
one, with these options: all the quick ones (first, marked `(Recommended)`), all of them,
and none for now. Say how long each choice takes in real units, for example "4 quick
tickets, about 5 minutes; 3 that need answers, about 10 minutes each."

## 4. Apply what was approved

- Re-read each ticket right before writing to it. Another session may have changed it since
  the review.
- **Close** with a comment that gives the reason and the evidence:
  `gh issue close <n> --reason "not planned" --comment "<reason>"`. Use `--reason completed`
  when the work is already done (link the commit), and `--duplicate-of <m>` for duplicates.
- **Update** by editing the body (`gh issue edit <n> --body-file <file>`). Keep the ticket's
  existing format and sections, and add a short comment that says what changed and why.
- **Re-order** with native dependencies where the tracker has them:
  `gh api --method POST repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by -F issue_id=<blocker-db-id>`
  to add, and `gh api --method DELETE repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by/<blocker-db-id>`
  to remove, where the database id comes from
  `gh api repos/{owner}/{repo}/issues/<blocker> --jq .id`. Keep any `## Blocked by` section
  in the body in step with the edges.
- **Split** by creating the new tickets first, then wiring their blocking edges in a second
  pass, once every ticket has a real number. Close the original with links to the new ones,
  or keep it as their parent.
- **Release** a stale claim with `gh issue edit <n> --remove-assignee <login>` and a comment.

## 5. Triage what the user picked

Triage the tickets the user picked in step 3, after step 4, so that closes and merges have
already landed. Work in this order, and restate progress as "ticket N of M" before each one.

1. **Quick** tickets. The user approved the drafts in step 3, so apply them: replace the
   title and body, remove the untriaged label, add the ready and category labels, wire the
   blockers, and add a short comment saying the ticket was shaped and what was decided.
2. **Not for an agent.** Swap the untriaged label for the human or needs-info label, and
   comment with what the ticket is waiting on.
3. **Needs answers** and **too big**, one ticket at a time. Shape each in place with the
   `new-ticket` skill's "shape an existing ticket" path: ask the questions, show the draft,
   and on approval rewrite the ticket and swap its label to ready. Without that skill, do
   those steps yourself. For a split, create the new tickets as in step 4.

Re-read each ticket right before writing to it. If the user stops partway, leave the rest
untriaged and list them in the report.

Do the triage yourself. Don't hand it to a `triage` skill, because in some setups only the
user can start one. You may name it in the report as something the user can run.

## 6. Make sure something is ready

Check what `next-ticket` would pick now. If at least one ready ticket is unblocked, go to
step 7.

If none is, and untriaged tickets are still open, don't end on "nothing is ready". Ask once
more, with the question tool, which untriaged ticket to triage now. Offer the smallest
first, marked `(Recommended)`, and include "None for now". On a pick, triage it as in
step 5.

## 7. Report

Give a short summary: how many tickets were checked, what was closed, updated, re-ordered,
split, released, or triaged, what was left untriaged or for the user, and the next three
tickets in the order next-ticket will now pick them.
