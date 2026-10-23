---
name: update-deps
description: Update every dependency in a repo across every language and ecosystem it uses (Python, Node.js, Go, Rust, Ruby, PHP, Java/Kotlin, .NET, Swift, Dart, Elixir, Deno, Terraform, Docker base images, git hooks, and anything else it finds), update GitHub Actions with actions-up, and on GitHub resolve the open Dependabot security alerts it can. Patch and minor updates go in together; each major update is tried on its own and kept only if tests, lint, and typecheck pass. Use when the user says "update dependencies", "update deps", "bump packages", "upgrade everything", "update github actions", "fix dependabot alerts", "fix security vulnerabilities in dependencies", or "are my deps out of date".
---

# Update dependencies

Bring every dependency up to date without breaking the project. Security fixes come first,
then safe updates, then major updates one at a time, then GitHub Actions. Every change is
proven by the project's own checks, and anything that breaks is reverted and reported, not
left half-done.

## 1. Inventory

1. **Start clean.** Run `git status`. If there are uncommitted changes, ask whether to
   continue on top of them, since reverting a failed update must not lose the user's work.
2. **Find every language the repo uses**, not just the ones you expect. List the file types
   (`git ls-files | sed -n 's/.*\.//p' | sort | uniq -c | sort -rn`) and find every manifest
   and lockfile, including in subdirectories, since monorepos and workspaces keep several.
   Each language with a manifest is an ecosystem to update.
3. **Look up the commands** for each ecosystem. Common ones:

   | Ecosystem | Manifest / lockfile | See what's outdated | Update within ranges | Major updates |
   |---|---|---|---|---|
   | Python (uv) | `pyproject.toml`, `uv.lock` | `uv tree --outdated --depth 1` | `uv lock --upgrade`, then `uv sync` | Raise the range in `pyproject.toml`, then `uv lock --upgrade-package <pkg>` |
   | Python (pip) | `requirements*.txt` | `pip list --outdated` in the project venv | Edit pins, reinstall | Edit pins |
   | Node (bun) | `package.json`, `bun.lock` | `bun outdated` | `bun update` | `bun update --latest <pkg>` |
   | Node (npm) | `package-lock.json` | `npm outdated` | `npm update` | `npm install <pkg>@latest` |
   | Node (pnpm) | `pnpm-lock.yaml` | `pnpm outdated` | `pnpm update` | `pnpm update --latest <pkg>` |
   | Node (yarn) | `yarn.lock` | `yarn outdated` | `yarn upgrade` | `yarn add <pkg>@latest` |
   | Deno | `deno.json`, `deno.lock` | `deno outdated` | `deno outdated --update` | `deno outdated --update --latest <pkg>` |
   | Go | `go.mod`, `go.sum` | `go list -u -m all` | `go get -u ./...`, then `go mod tidy` | New major = new module path (`/v2`): change the imports, then `go get` |
   | Rust | `Cargo.toml`, `Cargo.lock` | `cargo update --dry-run` | `cargo update` | Raise the version in `Cargo.toml`, then `cargo update <crate>` |
   | Ruby | `Gemfile`, `Gemfile.lock` | `bundle outdated` | `bundle update --conservative` | Raise the constraint in `Gemfile`, then `bundle update <gem>` |
   | PHP | `composer.json`, `composer.lock` | `composer outdated --direct` | `composer update` | `composer require <pkg>:^<new>` |
   | Java/Kotlin (Maven) | `pom.xml` | `mvn versions:display-dependency-updates` | `mvn versions:use-latest-releases -DallowMajorUpdates=false` | Edit the version in `pom.xml` |
   | Java/Kotlin (Gradle) | `build.gradle(.kts)`, `gradle/libs.versions.toml` | The project's versions plugin if it has one, else compare by hand | Edit versions or the version catalog | Same |
   | .NET | `*.csproj`, `Directory.Packages.props` | `dotnet list package --outdated` | `dotnet add package <pkg>` per package | Same, with the new version |
   | Swift | `Package.swift`, `Package.resolved` | `swift package update --dry-run` | `swift package update` | Raise the requirement in `Package.swift` |
   | Dart/Flutter | `pubspec.yaml`, `pubspec.lock` | `dart pub outdated` | `dart pub upgrade` | `dart pub upgrade --major-versions <pkg>` |
   | Elixir | `mix.exs`, `mix.lock` | `mix hex.outdated` | `mix deps.update --all` | Raise the requirement in `mix.exs` |
   | Terraform | `*.tf`, `.terraform.lock.hcl` | Compare provider/module constraints with the registry | `terraform init -upgrade` | Raise the constraint |
   | Docker | `Dockerfile*`, compose files | Compare base image tags with the latest | Edit tags within the major | Edit the tag |
   | Git hooks | `.pre-commit-config.yaml` | (the update shows it) | `prek update` | Same |
   | GitHub Actions | `.github/workflows/*.yml`, `action.yml` | `actions-up --dry-run --json` | See [step 5](#5-github-actions) | See step 5 |

   For an ecosystem that isn't listed, or a command you're not sure of, check the tool's
   `--help` or its official docs before running anything. Don't guess flags. Use the package
   manager the project already uses (from its lockfile, justfile, or agent instructions), and
   never switch package managers as part of an update.
4. **Note language and runtime versions** (`.python-version`, `.nvmrc`, `.tool-versions`,
   `mise.toml`, the `go`/`toolchain` lines in `go.mod`, `rust-toolchain.toml`, `engines` in
   `package.json`). Report newer ones, but don't change them unless the user asks, since a
   runtime upgrade affects every developer's machine and CI.
5. **Find the checks.** Get the test, lint, typecheck, and build commands from the
   justfile/Makefile, package scripts, agent instructions, or CI workflows. Run them once
   **before** changing anything, so failures that were already there aren't blamed on an
   update. Note any that fail.
6. **List what's outdated** in each ecosystem, split into patch/minor and major.

State the plan in one line before starting, for example "uv + bun + Go + GitHub Actions: 21
patch/minor, 4 major, 6 actions, 2 Dependabot alerts."

## 2. Dependabot alerts (GitHub repos)

If the repo has a GitHub remote, list the open alerts:

```bash
gh api --paginate 'repos/{owner}/{repo}/dependabot/alerts?state=open' --jq '.[] | {
  number, severity: .security_advisory.severity, summary: .security_advisory.summary,
  package: .dependency.package.name, ecosystem: .dependency.package.ecosystem,
  manifest: .dependency.manifest_path, scope: .dependency.scope,
  vulnerable: .security_vulnerability.vulnerable_version_range,
  patched: .security_vulnerability.first_patched_version.identifier }'
```

If the call fails with 403 or 404, alerts are turned off or the token can't read them. Say
so and continue with the other steps. Where a language has its own scanner and it's
installed (`govulncheck ./...`, `cargo audit`, `npm audit`, `pip-audit`), run it too, since it
catches what Dependabot doesn't cover.

Work the alerts from most to least severe:

- **Direct dependency:** raise it to at least the patched version, editing the manifest's
  range if the current range doesn't allow it.
- **Transitive dependency:** first update the direct dependency that pulls it in. If that
  isn't enough, upgrade just the package in the lockfile (`uv lock --upgrade-package <pkg>`,
  `bun update <pkg>`, `go get <module>@<version>`, `cargo update <crate>`). As a last
  resort, force the version (`overrides` in `package.json`, a constraint in `pyproject.toml`,
  a `replace` or `require` in `go.mod`) and add a comment saying which alert it fixes, so it
  can be removed later.
- **GitHub Actions alerts** are fixed in step 5.
- A security fix that needs a major update is still attempted, using the rules in step 4.
  If it can't be made to pass, report it as an open vulnerability, not a skipped update.
- **No patched version exists:** report the alert, the risk, and any workaround from the
  advisory.
- Never dismiss an alert. Alerts close on their own once the fix reaches the default branch.

Also list any open Dependabot pull requests (`gh pr list --app dependabot`). Report which
ones this run makes redundant, but don't close them.

## 3. Patch and minor updates

1. In each ecosystem, update everything within its current ranges (the "Update within
   ranges" column), and raise ranges for minor updates where the project pins tightly.
2. Update git hooks and Docker base images within their current major.
3. Run all the checks from step 1. If something fails, find the package that caused it (by
   reverting half of the updates at a time if needed), hold that package back, and note why.

## 4. Major updates, one at a time

For each major update, smallest blast radius first:

1. Read the package's changelog or migration guide for every major version crossed.
2. Update the package (the "Major updates" column) and make the code changes the migration
   guide calls for.
3. Run all the checks.
4. **Passing:** keep it. **Failing:** if the fix is small and clear from the migration guide,
   make it and re-run. Otherwise revert this package's changes completely (manifest,
   lockfile, and code), confirm the checks are back to passing, and report it with the reason
   and a link to the migration guide.

Don't move to the next major update until the current one is either kept or fully reverted.

## 5. GitHub Actions

Update actions with [actions-up](https://github.com/azat-io/actions-up). If it isn't
installed, run it with `bunx actions-up` (or `npx actions-up`). Set
`GITHUB_TOKEN=$(gh auth token)` so it isn't held to GitHub's 60-requests-an-hour limit.
Add `--recursive` if the repo keeps workflows or composite actions (`action.yml`) outside
`.github`.

1. **Keep the repo's pinning style.** Look at the existing `uses:` refs. If they're pinned to
   commit SHAs, use `--style sha` (the default). If they use tags like `@v4`, use
   `--style preserve`. Never switch a repo between the two as part of an update.
2. **Preview:** `actions-up --dry-run --json`. Each entry in `updates` with
   `isBreaking: true` is a major update. `runners` lists `runs-on` image upgrades.
3. **Patch and minor:** `actions-up --mode minor --yes --style <style>`.
4. **Majors:** read each action's release notes for every major crossed, and check that the
   inputs, outputs, and runtime each workflow uses still exist. Then apply them with
   `actions-up --yes --style <style> --exclude '^runner/'`, adding an `--exclude` for any
   action whose breaking change you can't safely adapt to. Make any input or output changes
   the release notes call for.
5. **Runner images** (`ubuntu-22.04` → `ubuntu-24.04`) change the whole build machine. Don't
   apply them by default. List them in the report for the user to decide.
6. **Check the workflows.** Run `actionlint` if it's installed. Workflows can't be run
   locally, so CI on the next push is the real test. List every major action update in the
   report so the user knows what to watch in that first run.

Respect `# actions-up-ignore` comments. They mark actions the project has pinned on purpose.

## 6. Verify like a user

Passing checks aren't enough. Run the app the way the user would: start the dev server and
load the main pages in a real browser, call the live API, or run the CLI's main commands.
Updated dependencies often break things at runtime that the tests miss. Then confirm every
lockfile changed alongside its manifest, and that `git diff` holds no stray files.

## 7. Report

Don't commit. Leave the changes for the user to review. Then report:

- **Security:** each Dependabot alert and scanner finding, and whether it was fixed,
  couldn't be fixed (and why), or has no patch yet.
- **Updated:** patch/minor counts per ecosystem, and each major update kept, with the code
  changes it needed.
- **GitHub Actions:** actions updated (minor and major, with any workflow edits), and runner
  image upgrades left for the user to decide.
- **Held back:** each package or action that wasn't updated, the error, and the migration
  guide link.
- **Runtimes:** newer language or runtime versions available, not applied.
- **Checks:** what ran before and after, and the results, including what you checked by hand.
- **Commits:** a suggested split, for example one commit per ecosystem, one for GitHub
  Actions, and one per major update, so a problem can be reverted on its own.
