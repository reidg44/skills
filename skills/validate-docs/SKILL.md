---
name: validate-docs
description: Audit every piece of documentation in a repo (README, AGENTS.md/CLAUDE.md, docs/, runbooks, docstrings-as-docs, examples) against the actual code and config, fix everything that is wrong, stale, or missing, and re-verify until the docs can be trusted. Verifies commands, file paths, code references, config keys, env vars, versions, links, layout trees, and code examples. Use when the user says "validate the docs", "check the docs are accurate", "are the docs up to date", "audit the README", "docs drift", or before a release. To record new learnings from a session, use wrap-session instead.
---

# Validate docs

Check that the repo's documentation tells the truth about the code as it is today, and fix it where it doesn't. The code is the source of truth. Never change code to match the docs unless the user asks.

## Phase 1: Inventory

1. **Find the docs.** In a git repo, use `git ls-files` so ignored files are skipped. Include:
   - Markdown and text docs: `README*`, `CONTRIBUTING*`, `CHANGELOG*`, `docs/**`, `*.md`, `*.mdx`, `*.rst`, `*.adoc`.
   - Agent instruction files: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules`, and similar. If `CLAUDE.md` only imports `@AGENTS.md`, check `AGENTS.md`.
   - Skill and prompt files (`SKILL.md`, prompt templates), since they describe how the project works.
   - Doc-like comments: module docstrings, `--help` text, and comments that describe usage.
   - Example and sample config: `.env.example`, `config.example.*`, `examples/**`.
2. **Skip** vendored code, `node_modules`, `.venv`, generated API docs, build output, and lockfiles. Treat `CHANGELOG` entries and ADRs/decision records as historical. They describe the past, so don't "fix" them to match today's code. Only check that the newest entry isn't missing obvious recent changes. Don't extend this to other docs: a README, guide, or diagram that is wrong is not "historical", it gets fixed or removed.
3. **Learn the ground truth sources.** Note where the real answers live: `justfile`/`Makefile`/`package.json` scripts, `pyproject.toml`/`Cargo.toml`/`go.mod`, CI workflows, entry points, config loaders, env var reads, and the directory tree.
4. **Scope.** Default to the whole repo. If the user names files or a directory, check only those (but still use the whole repo as ground truth). If they say "since the last release" or name a branch, prioritize docs that mention files changed in `git diff <ref>...HEAD`.

State the scope in one line before starting, for example "Checking 14 docs (README, AGENTS.md, docs/ ×11, .env.example) against the repo."

## Phase 2: Extract and verify claims

Go through each doc and pull out every checkable claim. Verify each one against the repo. If your tool supports sub-agents, split the docs into groups and check them in parallel. Give each agent its doc list, the ground-truth sources from Phase 1, and the checklist below. Tell agents to report findings, not edit files. If your tool doesn't support sub-agents, work through the docs one at a time yourself.

### Checklist

| Claim type | How to verify |
|---|---|
| **Commands** (`just x`, `npm run x`, `make x`, `uv run x`, CLI invocations) | The recipe/script/target exists with that name and arguments. For CLIs, check flags against `--help` or the arg parser source. Run a command only if it is read-only and fast (`--help`, `--version`, `just --list`, a dry run). Never run installs, deploys, migrations, or anything that writes outside the repo. |
| **File and directory paths** | The path exists. Moved files are a common source of drift, so if one is missing, search for its new location. |
| **Layout trees** (the ASCII directory diagrams) | Compare against the real tree. Flag both missing entries and important new ones. |
| **Diagrams** (Mermaid, PlantUML, Graphviz/DOT, D2, ASCII architecture or flow diagrams) | Check every node, edge, and label against the code: components and services exist, calls and data flows go the way the arrows say, sequence steps happen in that order, states and transitions match. A wrong diagram is a finding to fix, never "illustrative" or "historical". |
| **Code references** (functions, classes, modules, CLI subcommands, endpoints) | Search for the symbol. Check that names, parameters, and return shapes match what the doc says. |
| **Config keys and env vars** | Search for where the code reads them. Flag documented vars nothing reads, and vars the code reads that aren't documented. Check defaults match. Make sure `.env.example` lists every required var. |
| **Versions and requirements** (language version, tool versions, dependencies) | Compare with the manifest, lockfile, `.tool-versions`, CI matrix, or Dockerfile. |
| **Code examples** | Imports resolve, called functions exist with those signatures, and the example would actually run. Where it is safe and cheap, actually run it. |
| **Behavior claims** ("retries 3 times", "caches for 1 hour", "runs on commit") | Read the code that implements it and confirm the details. |
| **Links** | Relative links and `#anchors` point to files and headings that exist. Check external links only if the user asks or the tool can do it cheaply. Report dead ones, and don't guess replacements. |
| **Install and setup steps** | Walk through them in order against the repo. Every step needed is listed, nothing listed is obsolete, and the order works. |
| **Cross-doc consistency** | The same fact (a command, a version, a path) is stated the same way everywhere. Flag contradictions between docs. |
| **Staleness markers** | "TODO", "coming soon", "not yet implemented", "deprecated", and dated statements. Check whether they are still true. |

### Completeness (the "up to date" half)

Also look the other way, from the code to the docs:
- User-facing commands, scripts, CLI subcommands, or endpoints that no doc mentions.
- Required env vars or config with no documentation.
- Top-level directories or major components missing from the layout/architecture docs.
- Recent significant changes (`git log --since` the doc's last edit, via `git log -1 --format=%cs -- <doc>`) that the doc should mention but doesn't.

Only flag gaps a reader would actually hit. Not every internal helper needs docs.

### Finding format

Each finding gives: `doc:line`, the claim as written, what is actually true (with the `file:line` evidence), the proposed fix, and a confidence level (high, medium, or low).

## Phase 3: Fix

The goal is that, when you finish, every checkable claim in the docs is correct. Fix by default. Hand findings to the user only in the narrow cases below.

1. **Merge and verify.** Combine findings and remove duplicates. Re-check each one yourself against the evidence before editing. Don't trust a sub-agent's finding unchecked.
2. **Apply every fix where the code shows the truth.** That covers wrong commands, paths, names, versions, defaults, flags, behavior details, dead relative links, outdated layout trees, contradictions between docs, stale "TODO"/"coming soon" notes, and missing entries in command, env var, or config lists.
   - **Fill gaps too.** If a user-facing command, env var, or component is undocumented, add it in the doc's existing format. Keep additions as short as the surrounding entries.
   - **Update diagrams.** Edit Mermaid and other diagram source so it matches the code: rename, add, or remove nodes and edges, and fix arrow directions and step order. Keep the diagram's type and style. If a rendered image (`.png`, `.svg`) was generated from source in the repo, update the source and regenerate the image if the tool is available; otherwise flag the stale image. Never leave a wrong diagram in place with a note calling it outdated or historical.
   - **Remove what's dead.** Delete documentation for commands, files, options, or features that no longer exist.
   - **Delete obsolete docs.** Remove whole docs that no longer describe anything real: plans for finished or abandoned work, notes on removed features, old migration guides, scratch or session artifacts. Delete them rather than moving them to an `archive/` folder or adding a "historical"/"archived"/"deprecated" banner. Git keeps the history. Then fix or remove every link and reference to the deleted doc. CHANGELOG entries and ADRs are the exception (see Phase 1).
   - **Leave planning-system docs alone.** This targets stray docs only. If a doc belongs to a structured planning or spec workflow (BMAD, spec-driven development, PRDs, epics and stories, sprint tracking, or similar) and sits in that system's folders and format, don't delete it, even if the work it describes is finished. Those files are that system's record, and its tools may read them.
   - Match the doc's existing voice, format, and level of detail. Change the wrong fact, not the surrounding prose.
   - Fix every copy of a repeated fact so the docs stay consistent.
   - In agent instruction files, keep edits terse. They load into every session.
3. **Hold back only when the code may be wrong.** If a doc describes sensible behavior and the code looks like a bug, don't rewrite the doc to describe the bug. Report it as a possible code bug. Also ask before writing a new section longer than about a paragraph, or before deleting a doc when you can't tell whether it's still in use.
4. **If you can't edit a file** (permissions, sandbox), say so clearly and give the exact replacement text for each fix so the user can apply it.

## Phase 4: Re-verify

Don't stop at "I made the edits". Prove the docs are now correct.

1. **Re-check every edited claim** against the code, the same way as in Phase 2. A fix that introduces a new error is worse than no fix.
2. **Close out the "unverified" claims.** For claims about external tools (CLI flags, install commands, third-party config), check the tool's `--help` output or official docs where you can. Whatever still can't be checked goes on the unverified list in the report. Don't call it accurate.
3. **Run the checks.** Run the project's doc-related checks (markdown lint, link checker, docs build, a validate recipe, or the equivalent) and any hook that scans for secrets or PII, since edited docs are a common place for these to leak. If a check needs approval, ask for it. Don't skip it silently.
4. **Repeat** Phases 2-4 on the edited docs if the re-check found new problems.

## Phase 5: Report

Lead with a verdict, then the details:
- **Verdict:** one line on overall confidence, for example "High confidence: all 112 checkable claims verified against the code; 3 external-tool claims unverified (listed below)." Say "high confidence" only if every checkable claim was verified after the fixes and the checks passed.
- **Scope:** how many docs were checked, against what.
- **Fixed:** each change with `doc:line` and a one-line reason, grouped by type (commands, paths, config, versions, examples, diagrams, links, completeness).
- **Deleted:** each removed doc and why it was obsolete, so the user can restore it from git if they disagree.
- **Possible code bugs:** places where the doc looks right and the code looks wrong, with evidence.
- **Unverified:** claims that couldn't be checked, and why.
- **Checks:** which checks ran, and whether they passed.

Never commit, stage, or push the changes, even if the checks pass or a commit seems convenient. Leave every edit and deletion uncommitted so the user has time to review the diff first.
