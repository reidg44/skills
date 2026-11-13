---
name: generate-ideas
description: Study the current project and suggest ways to make it better, from ten-minute polish to big, hairy, audacious goals - faster code, better looks, smoother user experience, new capabilities, and "wouldn't it be really cool if" moonshots. Presents the ideas grouped by size, lets the user pick the ones they like, and files each pick as a needs-triage ticket. Changes no code. Works with GitHub issues or local markdown tickets. Use when the user says "generate ideas", "brainstorm", "what should I build next", "how could this be better", "I'm out of ideas", "give me ideas for this project", or asks for ideas about one area ("ideas to make it faster"). To capture an idea the user already has, use new-idea instead.
---

# Generate ideas

The user wants fresh ideas for the project they are working on. Read the project, come up
with a wide spread of ideas, show the best ones, and file the ones the user picks as tickets
for later triage.

This skill changes no code and starts on no idea. Its only output is the idea list and the
tickets the user asks for.

If the user named a focus ("performance", "the onboarding flow", "only big ideas"), keep
every step inside it, and drop the groups and lenses that don't apply.

## 1. Learn the project

Spend a few minutes reading, enough to say what the project does, who uses it, and how.
Ideas that could apply to any project are a sign this step was too thin.

- **What it is for:** README, docs, the agent instructions file, any roadmap or STATUS file.
- **How people use it:** the entry points, the screens, commands, or API a user touches, and
  the main path through them. For a project with a UI, look at the UI code and any
  screenshots. Run the app only if it starts in seconds and has no side effects.
- **Where it strains:** slow paths, repeated work, missing tests, rough error messages,
  manual steps, TODO and FIXME notes, dependencies doing little work.
- **Where it has been heading:** the last few weeks of commits.
- **What is already planned:** open tickets, so the list doesn't repeat them. Find the
  tracker the way step 4 describes.

In a large repo, split this reading across parallel subagents if the tool has them, one per
area, each returning observations, not ideas.

## 2. Generate widely, then choose

Write down at least 25 candidate ideas before choosing any. Go through each lens below and
ask what it suggests for this project:

- **Speed:** what the user waits for, and what the machine does twice.
- **Looks:** visual polish, consistency, motion, empty and loading states, output formatting.
- **Experience:** fewer steps, better defaults, clearer errors, first-run setup, undo,
  accessibility.
- **Trust:** reliability, recovery from failure, data safety, observability.
- **Reach:** new users, new platforms, integrations, sharing, an API or plugin surface.
- **Capability:** what the project could do that it can't today.
- **Maker's comfort:** build time, tests, tooling, anything that makes the project nicer to
  work on.
- **Delight:** the thing nobody asked for that would make someone show it to a friend.

Then push further for the ambitious end. Ask: what would this be with ten times the users,
or a tenth of the waiting? What would the user's favorite version of this do that sounds
unreasonable today? What does the project already have (data, position, a clever piece)
that could become something much larger?

Choose what to show:

- Keep ideas tied to something you saw in this project. Each one names its evidence.
- Drop ideas an open ticket already covers, and ideas the docs show were tried or rejected.
- Keep the spread. The list must include small and large ideas, practical and playful ones,
  and at least three lenses. Don't let one lens fill a group.
- Don't shrink the big ideas to make them sound safe. A moonshot can be unlikely. It can't
  be boring.
- Say what you don't know. A speed idea you haven't measured is a hunch: call it one.

Keep the candidates you don't show. The user may ask for more.

## 3. Present the ideas

Show 10 to 14 ideas in up to four groups, at most four per group, ordered from most to
least promising within each group. Leave a group out when you have nothing good for it.

1. **Quick wins:** an hour or less each.
2. **Solid upgrades:** an afternoon to a few days.
3. **Big bets:** weeks of work that would change what the project is.
4. **Wouldn't it be cool if:** playful or far-out ideas, each phrased as "Wouldn't it be
   cool if ...". Feasibility is not required here.

Number the ideas straight through, across groups, so the user can refer to them by number.
Give each idea three short lines:

```markdown
**3. Cache the parsed config between runs** (Speed)
Every command re-reads and re-validates all the config files before doing anything.
Why: startup is most of the wait for short commands. Unmeasured hunch. Size: about 2 hours.
```

- The first line is the title, starting with a verb, and the lens.
- The second line is what you saw in the project that prompted it.
- The third line is the payoff, how sure you are, and a size in real units.

Start the reply with one line saying what you read and how many ideas follow. Add no other
preamble, no recap, and no closing remarks.

Then ask which ideas to file, using the question tool: `AskUserQuestion` in Claude Code, or
the tool's equivalent, plain text only if there is none. Ask one multi-select question per
group, with each idea's number and title as an option, in a single call. Put the idea you
recommend most first in its group and mark it "(Recommended)". The user must also be able to
answer in free text: a list of numbers, "none", or "more".

- **"More", or a new focus:** show the next ideas from your kept candidates, generating new
  ones as needed, and ask again. Keep numbering from where the last round stopped, and never
  repeat an idea already shown.
- **A change to an idea ("3, but for the web UI only"):** file it the way the user worded it.
- **None:** stop. Don't file anything, and don't save the list to a file unless asked.

## 4. File the picks as tickets

Find the tracker: if `docs/agents/issue-tracker.md` exists, use its commands. If
`docs/agents/triage-labels.md` exists, take label names from it. Without these files, assume
GitHub and use `gh`. For a local-markdown tracker, tickets are files under
`.scratch/<feature>/issues/NN-<slug>.md`, with the state label on a `Status:` line.

For each picked idea:

1. Search open tickets once for a duplicate
   (`gh issue list --state open --search "<keywords>" --limit 10`). If an open ticket
   already covers the idea, add the idea to it as a comment instead of creating a ticket.
2. Create the ticket with the body below, passed on stdin
   (`gh issue create --title "<title>" --label needs-triage --body-file -`). For a local
   tracker, write one file numbered after the highest existing ticket in the feature folder
   the idea belongs to (or `.scratch/ideas/issues/` when it fits none), with
   `Status: needs-triage`. Don't stage or commit it.

Label every ticket `needs-triage` (or the name `docs/agents/triage-labels.md` maps it to),
never `ready-for-agent`: nobody has shaped these yet. Add `enhancement` when the tracker has
that label. If a label doesn't exist, create the ticket without it and say so in the report.

```markdown
## Idea

What would change, in a sentence or three. Describe behavior, not file paths or line
numbers, which go stale.

## Why

The payoff, and what in the project prompted the idea. Mark anything unmeasured or
uncertain as such.

## Size

The rough estimate in real units, and what it depends on.

## Open questions

- What triage should settle before this is built. For big bets and far-out ideas, include
  the smallest first step that would show whether the idea is worth pursuing.
```

If tickets can't be created (no tracker, not signed in, offline), say the cause and the fix
in one line, and include each picked idea's title and body in the reply so the user can file
them later.

## 5. Report

While filing more than three tickets, say "ticket N of M" as each one lands. Then reply
with:

1. One line per ticket: its link (or path), title, and label, at most five lines per group.
   Mark any that became a comment on an existing ticket.
2. Any failure, as cause and fix.
3. One next action: run `triage` or `new-ticket` on the pick you'd shape first, and name it.

If the `i-have-adhd` skill is active, its rules take precedence.
