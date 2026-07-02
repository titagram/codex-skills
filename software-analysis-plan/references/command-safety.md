# Command Safety

Classify project commands before running them. The skill may analyze and verify; it must not change application code or persistent target-repository state except for the final plan file.

## Safe By Default

These commands are generally safe after confirming they exist:

- Read-only shell inspection: `pwd`, `ls`, read-only `find` invocations, `rg --files`, `rg`, `sed -n`, `git status --short`, `git log --oneline -5`, `git diff --stat`. Do not use `find -delete` or mutating `find -exec` forms.
- Manifest inspection: reading `package.json`, `pyproject.toml`, `composer.json`, `Gemfile`, `go.mod`, `Cargo.toml`, config files, CI files, and docs.
- Test discovery commands that list tests without executing mutating setup, importing app code in a way that starts services, writing caches, connecting to databases, or running setup hooks.
- Lint, typecheck, unit test, integration test, and build commands only after script inspection shows they should not write tracked files, untracked artifacts, snapshots, coverage reports, caches, generated output, migrate data, deploy, seed, install, or call external services with side effects.

## Potentially Modifying

Treat these as unsafe in analysis mode. Do not run them; record relevant items as future implementation or verification steps in the final plan:

- Dependency installation: `npm install`, `pnpm install`, `yarn install`, `pip install`, `composer install`, `bundle install`, `go get`, `cargo update`.
- Formatters and fixers: commands containing `--write`, `--fix`, `format`, `prettier --write`, `eslint --fix`, `ruff --fix`, `black`.
- Generators: schema generation, client generation, route generation, asset builds that write target-repository output.
- Database operations: migrations, resets, seed scripts, fixture loading, local service bootstrap that changes data.
- Build or test commands that emit target-repository artifacts, snapshots, coverage reports, caches, or generated files. If such outputs are allowed, they must write outside the target repository, preferably under a temp directory, and the agent must confirm the target git working tree remains unchanged. Do not treat a user-approved disposable path inside the repository as safe.
- Commands that require credentials or call external APIs with side effects.

## Dangerous

Do not run these during this skill:

- Persistent git state changes: `git add`, `git commit`, `git merge`, `git pull`, `git switch`, `git checkout`, `git restore`, `git stash`, branch creation or deletion, index changes, worktree changes, and destructive git operations such as reset, checkout or restore of paths, clean, rebase, or forced branch changes.
- Database reset, truncation, destructive migration, production migration, or production seed.
- Deploy, publish, release, upload, payment, email, notification, or live service mutation commands.
- Secret, keychain, shell profile, system package, global runtime, daemon, or service changes.
- Commands outside the repository unless needed for read-only inspection.

## Execution Rules

- Check `git status --short` before and after running verification commands when the target is a git repository.
- `git status --short` may miss ignored artifacts. When running commands likely to create ignored output, inspect expected artifact or cache locations, or use ignored-file inspection such as `git status --short --ignored`, without deleting anything.
- Run the narrowest useful command first.
- Prefer dry-run, list, no-write, or output-outside-repo modes when available.
- If command behavior is unclear, read scripts and config before execution.
- If a command unexpectedly changes files, stop and report exact paths. This skill must not stage, revert, delete, overwrite, or clean up files as part of analysis. Record the incident in the final plan and final response, and ask the user to handle cleanup separately or start a different task.
- Record every command run, whether it passed, failed, was skipped as unsafe, or could not run.
