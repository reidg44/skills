# Best Practices for AGENTS.md / CLAUDE.md Files

_Researched November 20, 2026. Vendor behavior described here reflects the official docs on that date; tools change quickly, so re-check the linked sources before relying on a specific detail._

## The one rule

Keep the file short, and include only what the agent cannot work out by reading the repo. Everything else belongs in something that loads on demand (skills, path-scoped rules, nested files) or is enforced by the tool (hooks, deny rules, linters, CI).

Why: the file is loaded into every session, so every line takes a little of the agent's attention on every task, relevant or not. Long files cause rules to be quietly skipped.

## 1. What belongs in the file

Anthropic's test for each line:

1. Could the agent find this by reading the code?
2. Would it actually go and look?

If both are yes, leave it out. What usually passes:

- **Exact commands**: install, build, lint, typecheck, and how to run a single test file. Copy-pasteable, with the working directory if it matters.
- **Misleading spots in the code**: an old pattern that is everywhere but must not be copied, a directory that looks unused but isn't, generated paths that must not be hand-edited (and what to run instead).
- **Decisions that are not in the repo**: how deploys work, which helper the team settled on, what needs a human review or approval.
- **Definition of done**: which checks to run while iterating and which before finishing.
- **Environment gotchas**: required environment variables, services that must be running.
- **Anything you have had to correct twice.**

## 2. What to leave out

| Leave out | Why | Put it here instead |
|---|---|---|
| Architecture and file-layout tours | The agent reads the repo itself; the ETH Zurich study found these did not help agents find files faster | Nowhere, or existing docs |
| Generic advice ("write clean code", "follow best practices") | Adds length, changes nothing | Delete |
| Copies of existing documentation | Becomes a second source that drifts | A one-line pointer to the doc |
| Style and formatting rules | A tool does this for free and never forgets | Formatter, linter, pre-commit, CI |
| Standard language conventions | The model already knows them | Delete |
| Long step-by-step procedures | Only relevant to some tasks | A skill |
| Rules for one part of the codebase | Irrelevant most of the time | Path-scoped rule or nested file |
| Rules that can never be broken | The model only *usually* follows a written line | Hook, deny rule, or managed setting |
| Secrets, credentials, private operational details | The file is committed and widely read | Secret manager |
| Empty template sections | Noise | Delete |
| ALL-CAPS / "IMPORTANT" emphasis | Current models over-apply emphasized rules | Plain wording; shorten the file or use a hook |

## 3. Where everything else goes (Claude Code)

| Kind of content | Mechanism | How it loads |
|---|---|---|
| Facts needed in every session | `CLAUDE.md` | Always, in full |
| Multi-step procedures (release, runbook, doc style) | Skill: `.claude/skills/<name>/SKILL.md` | Name and description always; body only when used |
| Rules for certain files or folders | `.claude/rules/*.md` with `paths:` frontmatter | Only when the agent reads a matching file |
| Rules for a subproject | Nested `CLAUDE.md` in that directory | On demand, when the agent reads files there |
| Must-always / must-never actions | Hooks, `permissions.deny`, sandbox | Enforced by the tool, not the model |
| Things the agent learns as it works | Auto memory (`MEMORY.md`, v2.1.59+) | First 200 lines or 25 KB at session start |
| Access to outside systems | CLI tools or MCP servers | Tool names load; disable unused servers |

Things that commonly trip people up:

- **`@` imports do not save context.** Imported files are expanded at launch. They tidy the file but cost the same. Use skills or path-scoped rules to actually reduce what loads.
- **Rules in `.claude/rules/` without a `paths:` filter load every session**, exactly like `CLAUDE.md`.
- **CLAUDE.md is guidance, not enforcement.** If you keep strengthening a line and it is still missed, it belongs in a hook. The reverse also holds: a hook for a mere preference should be deleted.
- **Keep the enforced set small.** Every hook and deny rule occasionally misfires and needs maintaining.
- **HTML comments are stripped** before the file is loaded, so `<!-- maintainer notes -->` cost nothing.
- **After `/compact`**, the project-root file is reloaded; nested files reload only when the agent next reads a file in that directory; instructions given only in chat are lost.

## 4. User level vs. project level

Claude Code loads these layers broadest-first and adds them together (later layers do not replace earlier ones):

| Layer | Location | Use for | Shared with |
|---|---|---|---|
| Organization | Managed policy `CLAUDE.md` (deployed by IT) | Company-wide standards and compliance reminders | Everyone; cannot be excluded |
| User | `~/.claude/CLAUDE.md`, `~/.claude/rules/` | Your preferences in every project | Only you |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | What any teammate needs to work in this repo | Team, via git |
| Local | `./CLAUDE.local.md` (gitignored) | Your personal notes for this one repo | Only you |

How to decide where a line goes:

- **About you, and true in every repo** → user level. Examples: how you want answers written, tools you personally prefer, your review habits.
- **A new teammate would need it** → project level. Examples: commands, conventions, gotchas.
- **About you, in this repo only** → local. Examples: your sandbox URLs, your test data.
- **Must hold for the whole company** → organization level, with real enforcement done in managed settings rather than prose.

Keep the user-level file especially small. It loads in every project, including ones where its contents are irrelevant, and project-specific facts placed there are invisible to teammates.

Watch for conflicts across layers. Because layers are added together, two contradicting rules both reach the agent and it may pick either one.

## 5. AGENTS.md vs. CLAUDE.md across tools

AGENTS.md is the open, cross-tool format, stewarded by the Agentic AI Foundation under the Linux Foundation. Tool behavior differs:

| Tool | Reads | User-level file | Notes |
|---|---|---|---|
| Claude Code | `CLAUDE.md` only | `~/.claude/CLAUDE.md` | Does not read `AGENTS.md` directly |
| OpenAI Codex | `AGENTS.md` (and `AGENTS.override.md`) | `~/.codex/AGENTS.md` | One file per directory from repo root down to the working directory; 32 KiB combined cap by default |
| GitHub Copilot CLI | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | `$HOME/.copilot/copilot-instructions.md` | No general precedence defined among these files; avoid conflicts |
| Copilot cloud agent | `AGENTS.md` anywhere in the repo, plus the `.github` files | n/a | Nearest `AGENTS.md` in the tree wins |

Recommended setup for a multi-tool team:

1. Make `AGENTS.md` the single source of truth.
2. Give Claude Code a thin `CLAUDE.md` that imports it and adds only Claude-specific lines:

   ```markdown
   @AGENTS.md

   ## Claude Code
   - Use plan mode for changes under src/billing/.
   ```

   A symlink (`ln -s AGENTS.md CLAUDE.md`) also works on macOS and Linux.
3. Do not maintain separate hand-written copies per tool. Tools that read several of these files will see duplicates or contradictions.
4. If you use nested files, test each agent you rely on. They do not all handle the hierarchy the same way.

## 6. How to organize the file

- Use short markdown headers and bullets, not paragraphs.
- Make each rule specific and checkable: "Run `pnpm vitest run <file>` before committing" rather than "test your changes".
- Give a one-clause reason for non-obvious rules so the agent can apply them sensibly.
- Point to deeper docs with one line each instead of pasting them in.
- In monorepos, keep the root file universal and put package-specific guidance in nested files or path-scoped rules.

A file that passes the tests above tends to look like this:

```markdown
# Commands
- Install: pnpm install
- Run one test file: pnpm vitest run path/to/file.test.ts
- Typecheck: pnpm tsc --noEmit

# Conventions
- Use the error helpers in src/lib/errors.ts; never throw raw strings
- src/legacy/ is still live, but don't copy its patterns into new code

# Gotchas
- Integration tests need DATABASE_URL set; see .env.example
- src/gen/ is generated; edit the schema and run pnpm codegen instead

# More detail (read only when relevant)
- Release process: docs/release.md
```

## 7. How long

| Source | Guidance |
|---|---|
| Anthropic (official docs) | Under 200 lines per file; longer files reduce adherence |
| HumanLayer (practitioner blog, Nov 2025) | Under 300 lines; their own root file is under 60 |
| Agentic AI Foundation | No fixed number; keep only instructions that change what the agent does |

Treat line counts as a smoke alarm, not a target. The real test is whether each line changes behavior.

## 8. What the evidence says

- **ETH Zurich, "Evaluating AGENTS.md" (Feb 2026)**, the one rigorous study so far: auto-generated context files did not improve task success (slightly lower in most settings, not statistically significant) and raised cost by more than 20%. Human-written files did somewhat better than generated ones. Context files helped most where the repo had little other documentation. The authors recommend limiting files to details the agent cannot infer. Caveats: older models, Python repos.
- **Agentic AI Foundation five-run experiment (Aug 2026)**: on the harder task, some runs without a short AGENTS.md wasted time reorienting or ran an unrequested production build; none of the runs with the file did. One repo and one agent, so illustrative only.
- **GitHub's review of 2,500+ agent files (blog, pattern analysis rather than a controlled study)**: the useful files cover commands, testing, project structure, code style, git workflow, and boundaries, with concrete commands and examples instead of vague descriptions. Note this predates the ETH finding that structure tours add little.

Takeaway: a short, hand-curated file of non-obvious facts helps. A long or auto-generated one costs money and can hurt. If you start from `/init`, the work afterward is mostly deleting lines.

## 9. Maintenance

**Add a line when:**
- The agent repeats a mistake.
- Code review catches a convention it missed.
- You find yourself typing the same correction in a new session.
- A new teammate would need the same context.

**Remove or move a line when:**
- The repo changed (new package manager, moved directory) and the line is stale. Stale instructions can be worse than none.
- CI, a linter, or a hook now enforces it.
- It no longer changes what the agent does.

**Habits:**
- Review instruction files in pull requests like code.
- Audit periodically for contradictions across the user, project, local, and rules files.
- In Claude Code, `/memory` lists every instruction file that actually loaded, `/context` confirms what is in the session, and `/doctor prompt-audit` flags instructions that are outdated, point at missing files, or contradict each other.
- Check auto memory occasionally; it is plain markdown you can edit or prune.

## 10. Cleanup checklist

1. **Inventory.** List every file that loads: organization, user, project, local, rules, nested files, auto memory, plus AGENTS.md and Copilot instruction files.
2. **Delete.** Remove anything the agent can infer, anything generic, anything a tool enforces, and anything stale.
3. **Relocate.**
   - Procedures → skills
   - Area-specific rules → path-scoped rules or nested files
   - Zero-exception rules → hooks or deny rules
   - Long reference material → a linked doc
4. **Sort by scope.** Personal and universal → user. Team → project. Personal and repo-specific → local.
5. **De-duplicate.** One source of truth (AGENTS.md) with a thin CLAUDE.md import; resolve contradictions between layers.
6. **Tighten.** Rewrite survivors as specific, checkable bullets; drop emphasis words.
7. **Verify.** Start a fresh session, confirm what loaded, and run a typical task to see whether behavior changed.
8. **Keep it that way.** Add lines only in response to a repeated mistake; prune on a schedule.

## Sources

Official documentation
- Anthropic, "How Claude remembers your project": https://code.claude.com/docs/en/memory
- Anthropic, "Best practices for Claude Code": https://code.claude.com/docs/en/best-practices
- AGENTS.md specification site: https://agents.md
- OpenAI Codex, "Custom instructions with AGENTS.md": https://developers.openai.com/codex/guides/agents-md
- GitHub Copilot CLI, "Adding custom instructions": https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
- GitHub Copilot, "Adding repository custom instructions": https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions

Research
- Gloaguen et al., "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?" (ETH Zurich, Feb 2026): https://arxiv.org/abs/2602.11988
- InfoQ summary of the study: https://infoq.com/news/2026/03/agents-context-file-value-review/

Foundation and vendor blogs
- Agentic AI Foundation, "Writing an effective AGENTS.md" (Aug 2026): https://aaif.io/blog/writing-an-effective-agents-md
- GitHub Blog, "How to write a great agents.md: Lessons from over 2,500 repositories": https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/

Practitioner write-ups (opinion, not vendor guidance)
- HumanLayer, "Writing a good CLAUDE.md" (Nov 2025): https://www.humanlayer.dev/blog/writing-a-good-claude-md
