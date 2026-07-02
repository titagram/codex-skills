---
name: software-analysis-plan
description: Use only when the user explicitly invokes software-analysis-plan or asks to use this skill to analyze an existing software repository and create a path-aware production-readiness plan without modifying application code.
---

# Software Analysis Plan

Analyze an existing repository and create a concrete production-readiness plan. Do not implement the plan.

## Hard Constraints

- Proceed only when the user explicitly invokes this skill.
- Do not modify application code, configuration, assets, migrations, package manifests, lockfiles, tests, or generated project files.
- Create or update only the final plan file inside the analyzed target repository: `<target repo>/docs/production-readiness/YYYY-MM-DD-plan.md` (relative path `docs/production-readiness/YYYY-MM-DD-plan.md`). Creating `<target repo>/docs/production-readiness/` is permitted when needed for that file.
- Read files, inspect repository structure, inspect git state, and examine documentation freely.
- Discover stack, package manager, scripts, framework, and command behavior before running commands.
- Run only non-destructive verification commands after checking what they do; non-destructive means no persistent changes inside the target repository except the final plan file.
- Do not run install, migration, formatter, generator, deploy, seed, reset, or external mutation commands in analysis mode. Record them as future implementation or verification steps in the plan when relevant.
- Ask the user only for information that cannot be inferred from repository evidence or safe command output.
- Keep observed facts, assumptions, and unanswered decisions separate.

## Operating Loop

Reference links below are relative to the skill directory.

1. Confirm explicit invocation and state that application code will not be changed.
2. Inspect repository structure, README/docs, manifests, lockfiles, scripts, CI, deploy files, env samples, tests, database files, routes, entrypoints, and recent git state.
3. Read [discovery](references/discovery.md) and build an internal project dossier covering stack, architecture, implemented flows, command inventory, likely blockers, and missing context.
4. Read [command safety](references/command-safety.md) before running any project command.
5. Run relevant safe checks when available, such as lint, typecheck, tests, or build, only after script inspection shows they should not modify persistent project state. Skip build or test commands that write project artifacts, snapshots, coverage reports, caches, or generated output unless they can be configured to write outside the target repository, preferably to a user-approved temporary path. Record each command and result.
6. Read [production readiness audit](references/production-readiness-audit.md) and identify gaps across product/UX, frontend, backend/API, data, security, testing/QA, deploy/CI, observability, and documentation.
7. Read [questionnaire](references/questionnaire.md). Phase 1 always happens after discovery. Phase 2 is a required checkpoint: ask follow-ups when needed for a concrete plan, or explicitly conclude that no extra questions are needed.
8. Read [plan template](references/plan-template.md) and create `<target repo>/docs/production-readiness/YYYY-MM-DD-plan.md` using the current local date, with `docs/production-readiness/YYYY-MM-DD-plan.md` as the path relative to the analyzed target repository root.
9. Make the plan sequential and area-aware. Each task must include priority, objective, affected paths, what to change, how to change it, dependencies, acceptance criteria, and verification steps.
10. Final response must link the plan, summarize top priorities, list commands run, list any unexpected command-created modifications, and confirm that no application code was intentionally modified.

## Command Discipline

- Inspect script definitions before executing package scripts.
- Prefer read-only commands first: file listing, manifest inspection, test discovery, route discovery, and config inspection.
- Check git status before and after verification commands.
- If a command unexpectedly creates or modifies files, stop, report the exact paths, record the incident in the final plan when one is created and in the final response, and ask the user how to handle them. Do not stage or silently clean them.
- If a useful check cannot run safely, record why and include the next-best verification in the plan.

## Plan Quality Bar

The final plan must be specific enough for a later implementation agent to execute without repeating the whole analysis.

- Use concrete repository paths whenever possible.
- If an exact path cannot be known, give the most likely path and state what must be verified before implementation.
- Prioritize by launch risk, user value, implementation dependency, and confidence.
- Include product and UX completeness, not only technical infrastructure.
- Avoid generic production checklists detached from the repository.
