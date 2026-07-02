# Project Intake

Use this at the start of every `senior-project-execution` run.

## Inspect Before Editing

- Check `pwd`, repository root, branch name, and `git status --short`.
- Identify whether the branch appears dedicated. If it is clearly `main`, `master`, or a protected integration branch, ask before broad edits.
- Preserve unrelated local changes. If dirty files are relevant, inspect them carefully and work with them.
- Read top-level docs and manifests: `README*`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, package manifests, build config, test config, and app config.
- Map the project structure with `rg --files`, `find`, or framework-specific conventions.
- Identify the stack, entry points, data flow, important modules, and existing test locations.
- Identify how to run the project: install, lint, typecheck, test, build, preview, and smoke-check commands.

## Working Dossier

Keep a compact dossier in context:

- What the product does.
- Who the likely user is.
- Main workflows and screens.
- Key architecture boundaries.
- Available quality gates.
- Current risks or signs of neglect.
- Most promising improvement opportunities.

Do not create permanent documentation unless it directly helps the current task or the user requested it.
