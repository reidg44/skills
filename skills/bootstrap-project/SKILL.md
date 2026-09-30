---
name: bootstrap-project
description: Scaffold a new project/experiment repo the user's standard way - git, uv (Python), prek+betterleaks hooks, justfile, .gitignore with secrets excluded, README + AGENTS.md. Use when starting a new project, running /init on an empty repo, or when the user says "set up the project" / "new experiment".
---

# Bootstrap a new project

The user starts many short-lived experiment repos and wants each one set up the same way. Do it all in one pass, without asking about each piece.

## Standard scaffold

1. **git init** if not already a repo.

2. **Python projects: uv, never system Python.**
   ```bash
   uv init  # or create pyproject.toml manually
   uv venv  # .venv in project root
   ```
   Then replace the generated `pyproject.toml` with **`assets/pyproject.toml`** (in this skill dir): fill in `name`, `description`, and `dependencies`; keep the pytest + ruff config block verbatim. It's **application-style** (no `[build-system]`), which is the default. Only add a build backend + `[tool.hatch...]`/`[project.scripts]` if the user actually wants an installable package.
   Type hints, PEP 8, docstrings. Linter/formatter is **ruff** with `select = ["ALL"]` and the Google docstring convention, already configured in the template.
   ⚠️ Do NOT use `httpx`. Prefer `requests`/`aiohttp` (or stdlib) as appropriate.
   ⚠️ The user writes the Python application code themselves. Scaffold config/tooling, but do NOT author `.py` modules unprompted.

3. **Git hooks:** run the `prek-setup` skill (prek + betterleaks, `prek install -f`, `prek run --all-files`).

4. **.gitignore:** copy **`assets/gitignore`** (in this skill dir) to the project root as `.gitignore`. It's the toptal/VSCode generator output (visualstudiocode + macos + dotenv + python) and already covers `.env`, `.venv`, caches, build artifacts, etc. Its bottom "Custom rules" section adds the secret/credential excludes the generator omits (`*.pem`, `*.key`, certs, `credentials.json`, SSH keys). Keep those, and verify the secret block survived the copy. Add any project-specific downloaded third-party repos/assets there too.

5. **justfile** at the project root. Use `just` for common actions. Seed it with whatever applies: `build`, `test`, `run`, `lint`. Keep recipes short.

6. **README.md + AGENTS.md:**
   - README: what this is, how to set up and run. Assume a fresh MacBook: the user clones experiments onto multiple machines, so setup instructions must actually work.
   - AGENTS.md: project purpose, commands, gotchas. Keep it current and easy to append to, since sessions end with doc updates. Also create `CLAUDE.md` containing just `@AGENTS.md` so Claude Code, Codex, and Copilot all read the same instructions.

7. **Secrets pattern:** create `.env.example` with placeholder names. Tell the user to put real values in `.env` themselves. Never ask them to paste credentials into the chat.

8. **Optional (ask only if ambiguous): devcontainer.** If the user wants one: use the current official Claude Code devcontainer docs (https://code.claude.com/docs/en/devcontainer), remove the network firewall, include the `gh` CLI, and forward dev-server ports so localhost inside the container is reachable from the laptop.

## Finish

- If running in Claude Code, suggest `/claude-automation-recommender` for project-specific automations.
- First commit only when the user asks. Commits are signed and need the user at the keyboard.
