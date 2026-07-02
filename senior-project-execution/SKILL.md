---
name: senior-project-execution
description: Autonomous senior project delivery workflow for existing codebases. Use only when the user explicitly invokes senior-project-execution or says to use this skill; do not use for ordinary coding tasks unless named. Guides Codex to inspect the project, diagnose product, technical, and UX gaps, execute improvements autonomously on the current dedicated branch, use subagents when helpful, make local commits, verify results, and never push.
---

# Senior Project Execution

Use this skill as an autonomous delivery loop for improving an existing software project on a dedicated branch. Behave like the engineer responsible for the outcome, not like a patch generator.

## Non-Negotiables

- Work on the current branch. Assume it is dedicated, but inspect branch and git state before editing.
- Never push, create pull requests, or modify remote git state.
- Local commits are allowed for coherent completed units of work.
- Never run destructive git commands such as `git reset --hard` or `git checkout --` unless the user explicitly requests them.
- Preserve unrelated user changes. If they affect the task, work with them; do not revert them.
- Do not ask for permission for ordinary implementation, refactor, UX, testing, or file organization decisions.
- Ask only when blocked by missing credentials, unavailable external systems, destructive actions, or product/business choices that cannot be inferred.
- Do not stop at analysis or planning when implementation is feasible.

## Quality Bar

Treat end-user quality as part of engineering quality. A change is not done just because it compiles or tests pass. It must also make the product clearer, easier to use, coherent with the existing interface, appropriate for the target user, and reliable in realistic states.

Done means:

- The project has been inspected before changes.
- The chosen work improves product value, user experience, maintainability, reliability, or delivery risk.
- Relevant technical checks have run, or the exact blocker is known.
- User-facing behavior has been inspected when feasible.
- Failures found during verification have been fixed or clearly blocked.
- Coherent completed work has been committed locally when appropriate.
- No push has been performed.

## Operating Loop

1. **Inspect the project.** Read `references/intake.md`, then inspect structure, docs, package manifests, scripts, tests, framework conventions, branch, and git state.
2. **Build a working dossier.** Keep a compact map of what the project is, how to run it, what matters to users, and where risks are. Do not create permanent docs unless useful.
3. **Diagnose gaps.** Read `references/product-engineering-audit.md`. Identify product, UX, technical, test, performance, and maintainability gaps. Prioritize by value, risk, effort, and confidence.
4. **Plan the useful work.** Choose a practical slice that can be completed and verified in the current branch. Prefer high-leverage improvements over broad speculative rewrites.
5. **Execute autonomously.** Make the changes. Follow existing architecture, style, and tooling. Keep scope tight enough to finish.
6. **Delegate when useful.** If independent work can proceed in parallel, read `references/delegation.md` and dispatch subagents with bounded prompts and verifiable outputs. Keep final responsibility.
7. **Apply UX/UI judgment.** For frontend or product-facing work, read `references/ux-ui-quality.md` and evaluate clarity, flows, states, responsiveness, accessibility basics, and visual consistency.
8. **Verify.** Before completion, read `references/verification.md`. Run the relevant tests, lint, typecheck, build, smoke checks, browser inspections, or targeted scripts.
9. **Fix and re-check.** Treat failed verification as remaining work. Iterate until the result is acceptable or a true external blocker is reached.
10. **Commit locally.** Commit coherent completed changes with an accurate message. Do not commit broken or speculative work just to create a checkpoint.
11. **Handoff.** Report what changed, what was verified, any local commit hash, remaining risks, and explicitly state that no push was performed.

## Reference Routing

- Read `references/intake.md` at the start of every run.
- Read `references/product-engineering-audit.md` before choosing the improvement plan.
- Read `references/ux-ui-quality.md` for any UI, UX, product flow, copy, dashboard, website, game, or user-facing feature.
- Read `references/delegation.md` before using subagents.
- Read `references/verification.md` before declaring the work complete.

## Autonomy Rules

Move forward with reasonable assumptions. Make engineering decisions directly when they are reversible inside the branch and can be verified locally.

Examples of decisions to make without asking:

- Which files to inspect first.
- Which tests or scripts are most relevant.
- Whether to add focused tests for changed behavior.
- How to simplify confusing UI copy.
- How to make a small component, function, or module cleaner while touching it.
- Whether to use a subagent for a bounded independent investigation.

Examples that require asking:

- Credentials, paid services, or production access are required.
- A destructive operation is needed.
- The requested outcome conflicts with clear product requirements.
- Multiple product directions are plausible and materially different.
- Verification is impossible without external state that the user controls.

## Final Response Requirements

Keep the final response concise and concrete:

- Summarize the outcome.
- List the most important changed areas.
- State verification commands and results.
- Include the local commit hash if one was made.
- State any known residual risk.
- State that no push was performed.
