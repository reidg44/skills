---
name: new-idea
description: Capture a passing idea as a ticket in seconds, without interrupting the work in progress - no questions, no sizing, no grilling, no approval step, and no starting on the idea. The ticket lands as needs-triage so it gets shaped later. Works with GitHub issues or local markdown tickets, mid-session or as a side request. Use when the user says "new idea", "idea:", "jot this down", "note for later", "remind me to change", "capture this", or mentions in passing something they want to change later. For work the user wants shaped and ready to build now, use new-ticket instead.
---

# New idea

The user thought of something they want to change later and doesn't want to lose their
place. Write it down as a ticket and get out of the way. Speed matters more than polish:
the ticket gets shaped later, at triage.

Running this skill is the approval. Create the ticket without showing a draft first.

## Rules

- **Ask nothing.** No size check, no grilling, no draft approval. Where the idea is
  unclear, write your best reading and list what's unclear under `## Open questions` in the
  ticket. The one exception: if there is no idea to capture at all (nothing in the request
  and nothing in the recent conversation), ask for it in one plain-text line.
- **Don't start on it.** Don't edit code, write a plan, or research an approach for the
  idea. It is for later, and maybe for someone else.
- **Leave the session alone.** Don't change the task list, branch, staged files, or commits
  of the work in progress. Don't create scratch files: pass the ticket body on stdin.
- **Stay small.** Aim for three commands or fewer: one duplicate search, one create, and
  nothing else unless one of them fails.

## 1. Write the ticket

Take the idea from the user's words. Add what this session already knows that a later reader
would need: what the user was doing when the idea came up, and the feature, behavior, or
terms it refers to. Use what's already in the conversation. Don't go read code or docs to
fill it in.

- **Title:** a short phrase starting with a verb, under 70 characters.
- **Body:** the template below. Keep the user's own wording in `## Idea`. Describe behavior,
  not file paths or line numbers, which go stale.

```markdown
## Idea

What the user wants changed, in a sentence or three, close to their own words.

## Context

Where the idea came from: what was being worked on, and what prompted it. Leave this
section out when there is nothing to add.

## Open questions

- Anything unclear or undecided that triage should settle. Leave this section out when
  there is nothing.
```

## 2. Check for a duplicate

Find the tracker: if `docs/agents/issue-tracker.md` exists, use its commands. If
`docs/agents/triage-labels.md` exists, take label names from it. Without these files, assume
GitHub and use `gh`. For a local-markdown tracker, tickets are files under
`.scratch/<feature>/issues/NN-<slug>.md`, with the state label on a `Status:` line.

Run one search over open tickets
(`gh issue list --state open --search "<keywords>" --limit 10`).

- **An open ticket already covers this idea:** add the idea to it as a comment instead of
  creating a new ticket (`gh issue comment <n> --body-file -`).
- **A ticket is nearby but not the same:** create the new ticket and mention the neighbor
  in `## Context`.
- **The search fails or finds nothing:** create the ticket.

## 3. Create it

- Label it `needs-triage` (or the name `docs/agents/triage-labels.md` maps it to), not
  `ready-for-agent`. Nobody has shaped it yet, so `next-ticket` must not pick it up.
- Add `bug` or `enhancement` only when the idea makes the category obvious.
- **GitHub:** `gh issue create --title "<title>" --label needs-triage --body-file -`, with
  the body on stdin. If it fails because a label doesn't exist, create the ticket without
  that label and say so in the report.
- **Local tracker:** write one file, numbered after the highest existing ticket in the
  feature folder the idea belongs to (or `.scratch/ideas/issues/` when it fits none), with
  `Status: needs-triage`. Don't stage or commit it.

If the ticket can't be created (no tracker, not signed in, offline), don't lose the idea:
say the cause and the fix in one line, and include the title and body in the reply so the
user can file it later.

The same goes when you are running without tools, such as a side question that can only
answer from the conversation (`/btw` in Claude Code). Reply with the title and body, and
name the way to get it filed: in Claude Code, press `f` in the side-question overlay to
hand it to a background agent that has tools, or run the skill with `/subtask`.

## 4. Report and get back to work

Reply in two lines at most, with no preamble or recap:

1. The link (or path) and title of the ticket created or commented on, and its label.
2. The next action: run `triage` or `new-ticket` on it when ready to shape it.

If the skill ran in the middle of other work, pick that work up again right where it
stopped, without asking whether to continue.

If the `i-have-adhd` skill is active, its rules take precedence.
