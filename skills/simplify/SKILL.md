---
name: simplify
description: Review code for reuse, quality, and efficiency problems using three parallel reviewers, then apply the worthwhile fixes directly. By default it reviews the current diff; it can also sweep an entire codebase, a directory, or specific files when asked. Use when the user says "simplify", "simplify my changes", "simplify the whole codebase", "clean up this diff", "do a cleanup pass on this repo", or wants a cleanup pass before committing. For simplifying prose or documents, use plain-language instead.
---

# Simplify

Review code, find what can be reused, cleaned up, or made faster, and fix it. This is a quality pass, not a bug hunt. Don't change behavior.

## Phase 1: Decide the scope

Pick one mode from what the user said. Default to **diff mode**.

| User says | Mode | Scope |
|---|---|---|
| "simplify", "simplify my changes", nothing specific | Diff | Uncommitted changes |
| "the whole codebase", "the entire repo", "everything", "all of it" | Codebase | Every source file in the repo |
| names a directory, files, a commit, or a branch | Targeted | Exactly what they named |

State the mode and scope in one line before starting, for example "Codebase mode: 84 source files under `src/` and `scripts/`."

### Diff mode
1. **Inside a git repo:** run `git diff HEAD` to capture staged and unstaged changes. Also run `git status --porcelain` and include untracked files that are new source code, since `git diff` doesn't show them.
2. If there are no uncommitted changes, ask whether to review the last commit (`git show HEAD`), the branch (`git diff main...HEAD`), or the whole codebase. Don't guess.
3. **No git repo:** review the most recently modified source files, for example `find . -type f -mmin -60 -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/.git/*'`. Widen the window if nothing turns up, and tell the user which files you picked.

Review only what changed, plus the minimum surrounding code needed to understand it. If the diff is empty, say so and stop.

### Codebase mode
1. List the source files: `git ls-files` in a repo, otherwise `find` with the exclusions above.
2. Group them into areas (top-level packages, modules, or directories) so each area is small enough to review well. Note which areas hold shared helpers, since the reuse reviewer needs them for every area.
3. If the repo is large (roughly more than 50 source files or 10k lines), give each reviewer one area at a time instead of the whole repo, and work through the areas in order. Start with the code that changes most often (`git log --format= --name-only | sort | uniq -c | sort -rn | head`) or that the user cares about most.

### Targeted mode
Review exactly the files, directories, commit, or branch the user named. Treat a directory like a small codebase-mode run, and a commit or branch like diff mode.

### All modes
- Skip generated files, lockfiles, vendored code, migrations, fixtures, and build output.
- Read the project's agent instructions (`AGENTS.md`, `CLAUDE.md`, or similar) and any linter config, so reviewers judge against the project's own standards.

## Phase 2: Three reviewers in parallel

Run three independent reviews. If your tool supports sub-agents, start all three at once and give each one the scope (the diff, or the list of files in the area), the mode, and the project's coding standards. If it doesn't, do three separate passes yourself, one lens at a time, and don't let one pass bleed into another.

Tell each reviewer to:
- Search the whole codebase for context, but report findings only about code inside the scope.
- Return a list of findings. Each finding gives `file:line`, the problem, the proposed fix, and a confidence level (high, medium, or low).
- Report real issues, not style preferences the project doesn't enforce. Return an empty list if nothing is worth changing.
- Not edit any files.

In codebase mode, also tell reviewers to look across files: the same logic in several modules, competing helpers that do the same job, and patterns that are handled differently in different places.

### Reviewer 1: Code reuse
- Duplicated logic, within the scope or between the scope and other code, that should become one shared function.
- Code that re-implements an existing utility, helper, or standard-library function. Search the repo for existing helpers before flagging, and name the helper to use.
- Redundant blocks and repeated patterns.
- Chances to pull code into a reusable component or module. Flag these only when there are already two or more real call sites.

### Reviewer 2: Code quality
- Naming that is unclear or doesn't match the surrounding code.
- Functions that do too much, deep nesting, and control flow that is hard to follow. Early returns often help.
- Breaks from the coding standards in the project's agent instructions or linter config.
- Code smells: leaky abstractions, stringly-typed values that should be enums or types, needless indirection, dead code, and comments that repeat the code.
- Over-engineering: abstractions with one caller, config nobody sets, speculative generality, and premature optimization.

### Reviewer 3: Efficiency
- Unnecessary allocations, copies, and repeated computation, such as work inside a loop that could happen once outside it.
- Loops that should be batched, and per-item calls that a bulk API could replace.
- N+1 queries, and repeated file or network access that could be cached or combined.
- Independent I/O that runs one call at a time when it could run concurrently.
- Frontend code: unnecessary re-renders, unstable props or keys, and missing memoization where it measurably matters.

Only flag efficiency issues on paths that plausibly run often or on large inputs. A one-time setup script doesn't need tuning.

## Phase 3: Combine and fix

1. **Merge.** Collect all findings and remove duplicates. When two reviewers flag the same lines, keep the clearer fix.
2. **Filter.** Drop a finding when:
   - it would change behavior or public interfaces the user didn't ask to change,
   - it's a false positive (check the code yourself, don't trust the reviewer),
   - it's low confidence and the gain is small,
   - it touches code outside the scope, unless a small change there is required for a fix inside it,
   - or two findings conflict. Pick one and note why.
3. **Apply.** Make the remaining fixes directly. Match the surrounding code's style. Keep each change small and easy to review.
   - **Codebase mode:** apply fixes one area at a time and run the checks (step 4) after each area, so a failure is easy to trace. Do the high-impact fixes first. If the full set would touch so many files that the result is hard to review (roughly more than 20), apply the high-confidence, high-impact fixes and list the rest under "Not applied" for the user to choose from. Cross-module refactors, like merging competing helpers or moving shared code into a new module, go under "Not applied" unless they are small and safe.
4. **Verify.** Run the project's tests, linter, and type checker (check the `justfile`, `package.json`, `Makefile`, or agent instructions for the commands). If something fails because of a fix, repair it or revert that fix. Never leave the code worse than you found it.
5. **Report.** Give a short summary:
   - **Scope:** the mode, and how many files or areas were reviewed.
   - **Changed:** each fix with `file:line` and a one-line reason, grouped by reuse, quality, and efficiency.
   - **Not applied:** worthwhile findings left for the user (codebase mode), each with `file:line` and the proposed fix.
   - **Skipped:** findings you rejected, and why, in one line each.
   - **Checks:** which tests and linters ran, and whether they passed.

Don't commit. Leave the changes for the user to review.
