---
name: audit-agent-files
description: Run a full audit of every agent instruction file that loads for a project (AGENTS.md, CLAUDE.md, CLAUDE.local.md, .claude/rules, nested files, Copilot and Codex instruction files, user-level files, auto memory) against current best practices, then present a numbered list of suggestions - delete, move to a skill or path-scoped rule, turn into a hook, fix stale lines, de-duplicate, tighten, or add what is missing - and apply only the ones the user picks. Use when the user says "audit my agent files", "clean up CLAUDE.md", "clean up AGENTS.md", "my CLAUDE.md is too long", "review my agent instructions", "prune the instructions", or after running /init. To check docs for factual accuracy against the code, use validate-docs instead.
---

# Audit agent files

Agent instruction files load into every session, so every line costs attention on every task. Audit them against `references/best-practices.md`, suggest changes, and apply only what the user picks. Read that reference before Step 2.

Change nothing until the user has picked. These files steer every future session, so the user decides each change.

Report progress as "Step N of 5" at the start of each step.

## Step 1 of 5: Inventory

List every instruction file that loads for this project. Check each path; include only files that exist.

- **Project, shared:** `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `AGENTS.override.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.claude/rules/*.md`, and nested `AGENTS.md`/`CLAUDE.md` in subdirectories (use `git ls-files` so ignored and vendored files are skipped).
- **Project, personal:** `CLAUDE.local.md`. Confirm it is gitignored.
- **User level:** `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md`, `~/.codex/AGENTS.md`, `~/.copilot/copilot-instructions.md`.
- **Auto memory:** the project's memory index (`MEMORY.md`) and files, if the tool keeps one.
- **Imports:** follow every `@path` import and symlink, and note which file is the real source.

Also note what already enforces rules, so you can spot prose that duplicates it: formatter and linter config, pre-commit/prek hooks, CI workflows, and agent settings (hooks, `permissions.deny`).

For each file record: path, layer (user, project, local, rules, nested, memory), which tools read it, line count, byte size, and whether a `.claude/rules` file has a `paths:` filter.

Show the inventory as one short table, then one line on scope, for example "Auditing 6 files, 412 lines total, against the repo." Skip files the user excludes.

## Step 2 of 5: Audit

Go through every line of every file. If your tool supports sub-agents, split the files across them and run in parallel; give each the reference doc, the inventory, and the checks below, and tell them to report findings, not edit. Re-check each sub-agent finding yourself before listing it.

Run these checks:

1. **Inferable.** Could the agent find this by reading the repo, and would it look? Architecture tours, file-layout trees, and descriptions of what the code does usually fail. → delete.
2. **Generic.** "Write clean code", standard language conventions, advice any model already follows. → delete.
3. **Enforced elsewhere.** Style and formatting a linter or formatter already handles; rules a hook, CI job, or deny rule already enforces. → delete.
4. **Should be enforced.** Zero-exception rules ("never", "always", ALL-CAPS, "IMPORTANT", lines repeated in stronger words). → suggest a hook, deny rule, or CI check, and plain wording if the line stays. Also flag hooks that enforce a mere preference.
5. **Stale.** Verify every command, path, script, tool, env var, and version the file names against the repo: the recipe exists, the path exists, the package manager matches the lockfile. Stale lines are worse than none. → fix or delete.
6. **Procedure.** Multi-step workflows only some tasks need (release, deploy, runbook). → move to a skill.
7. **Area-specific.** Rules for one directory, package, or file type. → path-scoped rule (`.claude/rules/*.md` with `paths:`) or a nested file.
8. **Wrong layer.** Personal preferences in the project file → user or local. Project facts in the user file → project. Personal, repo-only notes in a shared file → `CLAUDE.local.md`.
9. **Duplicated or conflicting.** The same fact in two files, or two layers that contradict each other (layers add together, so both reach the agent). Hand-maintained copies per tool instead of one `AGENTS.md` plus a thin `CLAUDE.md` with `@AGENTS.md`. → one source of truth.
10. **Copied docs.** Content pasted from README or docs. → replace with a one-line pointer.
11. **Secrets and private details.** Credentials, internal hostnames, IPs, personal data in a committed file. → remove; flag as high priority.
12. **Vague.** Rules that can't be checked ("test your changes"). → rewrite as a specific command or condition, with a one-clause reason if the rule is non-obvious.
13. **Noise.** Empty template sections, emphasis words, paragraphs that should be bullets.
14. **Size.** Any file over 200 lines, a `.claude/rules` file with no `paths:` filter carrying area-specific rules, `@` imports used to "save context" (they don't), and Codex files over 32 KiB combined.
15. **Missing.** What a new teammate would need that no file says: exact install/build/lint/typecheck/single-test commands, the definition of done, required env vars or services, generated paths not to hand-edit, misleading spots in the code. Also corrections that appear more than once in auto memory or feedback notes, which belong in the instruction file. Suggest only additions the repo proves are true.

## Step 3 of 5: Suggestions

Write one numbered list of suggestions, numbered across all groups. Each suggestion gives:

- the number and a short title,
- `file:line`,
- the change: delete, move (and where), replace (with the exact new text), or add (with the exact text and where),
- why, in one clause, tied to a check from Step 2.

Group by action, highest impact first within each group: **Fix or remove** (secrets, stale, conflicts), **Delete** (inferable, generic, enforced elsewhere, noise), **Move** (skills, path-scoped rules, nested files, other layers, hooks), **Tighten** (vague, emphasis, copied docs), **Add** (missing). Combine identical changes across many lines into one suggestion ("Delete the layout tree, lines 12-48"). Show at most 5 suggestions per group in chat; if a group has more, put the rest in the next question batch rather than dropping them.

Lead with one line of totals, for example "18 suggestions; applying all would cut 412 lines to about 140."

If there are no suggestions, say so in one line, show the line counts, and stop.

## Step 4 of 5: Ask which to apply

Ask using the question tool: `AskUserQuestion` in Claude Code, or the tool's equivalent, plain text only if there is none. Ask one multi-select question per group, with each suggestion's number and title as an option and its `file:line` and why in the option description. Put the suggestion you recommend most first in its group and mark it "(Recommended)". If a group has more options than the tool allows per question, split it across questions ("Delete, 1 of 2"), and use further calls if there are more questions than one call allows.

The user must also be able to answer in free text: a list of numbers, "all", "all in <group>", or "none". Without a question tool, ask for the numbers in one plain-text message.

If the user picks none, stop with the line counts and no edits.

## Step 5 of 5: Apply and verify

1. **Apply each picked suggestion**, exactly as listed. Keep wording terse; change only the targeted lines.
   - **Moves:** create the destination (skill `SKILL.md` with `name` and `description`, a `.claude/rules/*.md` file with `paths:` frontmatter, a nested file, or a line in the other layer's file) before removing the original.
   - **Hooks and deny rules:** add them to the agent's settings file at the level that matches the rule (project for team rules, user for personal ones), and test that a hook runs before removing the prose line.
   - **User-level files** live outside the repo. Edit them only if picked, and say so in the report.
   - **Conflicts with two plausible answers:** ask which one wins before editing.
2. **Verify.**
   - Re-read each edited file. Every `@` import, link, and pointer resolves; every command and path still exists.
   - Recount lines and bytes per file.
   - Run the project's validate, lint, and secret or PII hooks if it has them. If a check fails, report the cause and fix it.
   - For moved content, confirm the destination loads the way intended (skill description triggers on the right request, `paths:` glob matches real files).
3. **Report.** Lead with the result, for example "Applied 12 of 18: 412 lines → 151 across 5 files." Then:
   - **Applied:** each by number with `file:line`, at most 5 per group, the rest summarized as a count.
   - **Skipped:** the numbers not picked, in one line.
   - **Outside the repo:** any user-level file or settings changed.
   - **Checks:** which ran and whether they passed.

   End with one next action: start a fresh session and confirm what loaded (in Claude Code, `/memory` lists the loaded files and `/context` shows their size), then run a typical task.

Never commit, stage, or push. Leave every edit for the user to review in the diff.

If the `i-have-adhd` skill is active, its rules take precedence.
