# Bootstrap Prompt

Use this prompt when asking another LLM to create project-specific operating rules from scratch.

````markdown
Create a project-specific operating structure for this software workspace.

Workspace root:

```text
[PROJECT_ROOT]
```

Project name:

```text
[PROJECT_NAME]
```

Goal: create an operating manual for future LLMs and developers. The result should include project-specific rules, source-of-truth guidance, documentation indexes, verification commands, and a logbook. Derive rules from the real project; do not invent architecture, commands, APIs, or conventions.

## Constraints

- Do not modify application code during this bootstrap unless explicitly asked.
- Before writing files, perform read-only discovery.
- Distinguish verified facts, reasonable inferences, unknowns, and proposals.
- Prefer existing project conventions over generic best practices.
- Do not run destructive commands, migrations, deploys, resets, or production operations.
- If existing instructions conflict, follow the most specific user/repository instruction.

## Discovery

Inspect:

- root docs: `README*`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `docs/`, `wiki/`, ADRs, changelogs, logbooks;
- runtime files: Docker, Makefile, package manager files, language config, CI config;
- source layout: top-level modules, entrypoints, tests, scripts, migrations, assets;
- commands: install, run, test, lint, build, audit, debug;
- risks: legacy dependencies, missing docs, missing tests, generated files, data sensitivity, fragile setup.

Summarize findings before writing files.

## Create or update

Create only files that fit the project:

```text
AGENTS.md
docs/README.md
docs/PROJECT_OVERVIEW.md
docs/ARCHITECTURE.md
docs/CODING_STYLE.md
docs/RUNTIME.md
docs/TESTING.md
docs/SOURCE_OF_TRUTH.md
docs/MAINTENANCE.md
docs/LOGBOOK.md
docs/indexes/README.md
docs/indexes/ROUTES_OR_ENTRYPOINTS.md
docs/indexes/DATA_MODEL.md
docs/indexes/SIDE_EFFECTS.md
docs/indexes/DEPENDENCIES.md
docs/indexes/SECURITY.md
scripts/docs_audit.py
```

If a file does not apply, omit it and explain why.

## `AGENTS.md`

Write the primary instructions for future agents:

- workspace scope;
- task classification;
- required initial reading;
- rules for new projects;
- rules for existing projects;
- architecture/style rules;
- anti-regression workflow;
- source-of-truth rules;
- documentation update rules;
- runtime/CI/test rules;
- security/data rules;
- logbook rules;
- forbidden actions without explicit approval;
- final checklist.

Make rules concrete. Use verified paths and commands. Mark unverified items as "to verify".

## Documentation rules

For each generated doc:

- include evidence where possible;
- avoid vague best-practice filler;
- document known gaps;
- keep future agent instructions actionable;
- record the bootstrap in `docs/LOGBOOK.md`.

## Audit

Create a lightweight docs audit script, preferably:

```bash
python3 scripts/docs_audit.py
```

The audit should check required files, local Markdown links, placeholders, and basic logbook structure.

## Final response

Report:

- files created or updated;
- sources read;
- rules generated;
- validations run;
- unresolved unknowns;
- suggested next steps.
````
