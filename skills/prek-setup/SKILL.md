---
name: prek-setup
description: Set up or migrate a repo's git hooks to a standard setup - prek (NOT pre-commit) with betterleaks (NOT gitleaks) for secret scanning. Use when adding pre-commit hooks to a repo, migrating from pre-commit/gitleaks, or when the user mentions prek, betterleaks, or commit hooks.
---

# prek + betterleaks setup

The standard for every repo: **prek** as the hook runner (drop-in replacement for pre-commit, same `.pre-commit-config.yaml` format) and **betterleaks** instead of gitleaks for secret scanning. Never suggest `pre-commit install`; never add gitleaks.

## Steps

1. **Check current state.** Look for `.pre-commit-config.yaml`. If it references `gitleaks`, that hook gets replaced with betterleaks. If the repo was set up with `pre-commit install`, the old hook in `.git/hooks/pre-commit` will be overwritten in step 3.

2. **Write/update `.pre-commit-config.yaml`.** Keep existing hooks (ruff, formatting, etc.) and ensure the secret scanner is betterleaks. If unsure of the current betterleaks repo URL/rev, search the web for "betterleaks pre-commit hook". Do not guess a rev.

3. **Install and run:**
   ```bash
   prek install -f        # -f overwrites any old pre-commit-managed hook
   prek run --all-files
   ```

4. **Fix failures before declaring done.** Common ones:
   - ruff formatting failures on first run: let the hook fix or run `ruff format`, then re-run.
   - False-positive secret findings on mock/test keys: add a betterleaks allowlist/exemption for the specific file+line (e.g. a mock API key in a test file). Never disable the scanner wholesale.

5. **Verify:** `prek run --all-files` exits clean. Report which hooks are active.

## Notes

- Python repos use `uv`. If ruff is involved, it's configured in `pyproject.toml`.
- If the user pastes a pre-commit config from elsewhere, silently convert gitleaks→betterleaks and mention it.
