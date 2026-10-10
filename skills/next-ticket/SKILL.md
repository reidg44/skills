---
name: next-ticket
description: Pick the next unblocked agent-ready GitHub issue (lowest number whose "Blocked by" issues are all closed) and take it end to end - read the ticket, build it test-first, verify it like a user would, commit, and close the issue so the next ticket unblocks. Use when the user says "next ticket", "pick up the next issue", "work the backlog", "grab the next ready-for-agent issue", or names an issue number to implement end to end.
---

# Next ticket

Pick up the next ticket and get it done. This works best in a fresh session. Each ticket
should say everything needed to build it, so don't count on context from earlier sessions.

The issue tracker is the only state. Tickets carry a label that marks them ready for an
agent (default `ready-for-agent`) and a `## Blocked by` section that lists the issues they
depend on. Closing a ticket is what unblocks the next one.

This skill works best alongside the `mattpocock-skills` plugin (github.com/mattpocock/skills).
Its `to-tickets` skill writes tickets in exactly this format. Its `tdd` and `code-review`
skills cover the build and review steps below. Without it, follow the steps as written.

## 1. Pick the ticket

If the user named an issue number, use that one and skip the blocker check. Otherwise list
the candidates:

```bash
gh issue list --state open --label ready-for-agent --limit 200 --json number,title,body \
  --jq 'sort_by(.number) | .[] | {number, title, body}'
```

If the project uses a different label (check AGENTS.md/CLAUDE.md or `gh label list`), use that.

For each candidate, lowest number first, read its `## Blocked by` section. Pick the first one
whose blockers are all **closed** (`gh issue view <n> --json state`). "None" or a missing
section counts as unblocked. A blocker in another repo (`owner/repo#n`) needs `--repo`.

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
