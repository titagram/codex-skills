---
name: bootstrap-workspace-rules
description: Create or update project-specific workspace operating rules and documentation scaffolds for Codex, other LLMs, and developers. Use when the user asks to create AGENTS.md, onboarding/governance docs, source-of-truth rules, logbooks, technical indexes, documentation audit scripts, or an organizational structure for any new or existing software workspace.
---

# Bootstrap Workspace Rules

Create a project-specific operating system for future LLM and developer work. Derive rules from the real workspace; do not invent architecture, commands, or conventions that are not observed or explicitly requested.

## Workflow

1. **Establish scope**
   - Use the current working directory as the workspace root unless the user gives another root.
   - Respect existing `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, direct user instructions, and repository-specific rules.
   - If the user asks only for a prompt or plan, do not write files.

2. **Run read-only discovery**
   - Inspect root docs, package/build files, Docker/CI files, test config, scripts, and top-level source directories.
   - Prefer `rg --files`, `rg`, `find`, `ls`, and package-manager metadata before deep-reading code.
   - Identify stack, runtime, commands, test surfaces, docs, modules, data model, entrypoints, side effects, and fragile areas.
   - Mark each finding as verified, inferred, or unknown.

3. **Choose the scaffold**
   - For an existing project, create only docs and scripts that fit the observed structure.
   - For a new or empty project, create conservative starter rules and label them as proposed until implementation exists.
   - Avoid empty ceremonial files; every file should guide future work.

4. **Create or update core files**
   - `AGENTS.md`: primary instructions for future agents.
   - `docs/README.md`: navigation for operational docs.
   - `docs/PROJECT_OVERVIEW.md`: purpose, modules, known status.
   - `docs/ARCHITECTURE.md`: observed architecture with evidence.
   - `docs/CODING_STYLE.md`: style derived from existing code.
   - `docs/RUNTIME.md`: install, run, environment, Docker/CI notes.
   - `docs/TESTING.md`: test commands, coverage, gaps.
   - `docs/SOURCE_OF_TRUTH.md`: precedence of code, docs, schema, tests, and generated artifacts.
   - `docs/MAINTENANCE.md`: task workflow from discovery to final verification.
   - `docs/LOGBOOK.md`: operational history template and first entry.
   - `docs/indexes/*.md`: route/entrypoint, data model, side effect, dependency, and security indexes when relevant.
   - `scripts/docs_audit.py`: lightweight docs audit, adapted from this skill when useful.

5. **Write strong rules**
   - Use concrete commands and paths when verified.
   - Write "do this" rules only when supported by evidence or explicit user preference.
   - Write "proposal" or "to verify" for conventions that are reasonable but unconfirmed.
   - Include anti-regression checks: search all uses, map downstream effects, verify behavior, document skipped checks.
   - Include "do not" rules for destructive commands, dependency upgrades, production data, broad refactors, and unverified assumptions.

6. **Validate**
   - Run the generated or bundled audit script:
     ```bash
     python3 scripts/docs_audit.py
     ```
     or:
     ```bash
     python3 <skill-dir>/scripts/docs_audit.py --root <workspace>
     ```
   - Run existing non-destructive checks if they are already documented or obvious.
   - Report any checks not run and why.

## Reference Prompt

When the user wants a ready-to-paste prompt for another LLM, read `references/bootstrap-prompt.md` and adapt it to their workspace.

## Bundled Script

Use `scripts/docs_audit.py` as a generic audit helper. It checks required operating-doc files, local Markdown links, unresolved placeholders, and basic logbook presence. Copy it into the target workspace only when the user wants a project-local audit command; otherwise run it from the skill folder with `--root`.

## Final Response

List created or updated files, verified sources, generated rules, validation commands, unresolved unknowns, and recommended next steps. Keep the response factual; distinguish verified findings from inferred structure.
