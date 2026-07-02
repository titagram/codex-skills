# Discovery

Build a compact project dossier before asking the user questions or writing the plan.

## First Pass

- Run `pwd`; run `git status --short` only when the directory is a git repository, or tolerate failure in non-git directories.
- List files with `rg --files` when available.
- Identify README files, docs, package manifests, lockfiles, framework config, CI files, deploy files, Docker files, environment samples, tests, migrations, seed files, and scripts.
- Inspect recent git history with `git log --oneline -5` when the directory is a git repository.
- Note unrelated local changes and avoid touching them.

## Stack And Runtime

Identify the language, framework, runtime, and package manager from evidence:

- JavaScript or TypeScript: `package.json`, lockfiles, framework config, `src/`, `app/`, `pages/`, `vite.config.*`, `next.config.*`, `tsconfig.json`.
- Python: `pyproject.toml`, `requirements*.txt`, `Pipfile`, `manage.py`, `app.py`, `src/`, `tests/`.
- PHP/Laravel: `composer.json`, `artisan`, `app/`, `routes/`, `database/migrations/`.
- Ruby/Rails: `Gemfile`, `config/routes.rb`, `app/`, `db/migrate/`.
- Go: `go.mod`, `cmd/`, `internal/`, `pkg/`.
- Rust: `Cargo.toml`, `src/`.
- Mobile or desktop: native project files, platform folders, build manifests.

Use the repository's own conventions over generic assumptions.

In monorepos or workspaces, identify package and app boundaries before assuming one root package manager or one deploy target.

## Product Surface

Infer implemented behavior from:

- Routes, pages, screens, components, controllers, API endpoints, server actions, handlers, jobs, commands, and domain models.
- Tests, fixtures, seed data, stories, screenshots, docs, and sample data.
- Auth, billing, onboarding, admin, notification, import/export, reporting, and support flows when present.

Record the primary user journeys that appear implemented, partially implemented, or absent.

## Command Inventory

Before running commands:

- Inspect manifest scripts and tool config.
- Identify lint, typecheck, test, build, format, migration, generation, seed, deploy, and dev server commands as inventory only.
- Classify commands with `references/command-safety.md` guidance; classification records risk and does not grant permission to run risky commands during discovery.
- Keep risky command categories as inventory for the final plan unless command-safety guidance explicitly classifies a narrow verification command as non-destructive.
- Prefer commands that verify behavior without writing persistent project state.

## Dossier Shape

Keep these notes in context; do not create a separate dossier file unless the user asks:

- Project name and purpose inferred from files.
- Stack, package manager, runtime, and app entrypoints.
- Main product flows and current completeness.
- Important directories and ownership boundaries.
- Data model, auth model, external integrations, background jobs, and deployment target if present.
- Available safe commands and skipped risky commands.
- Observed failures, missing tests, missing docs, and production blockers.
- Unknowns that require the user questionnaire.
