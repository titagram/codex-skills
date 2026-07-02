# Verification

Use this before declaring completion.

## Choose Relevant Checks

Prefer the repo's own commands and documented workflow. Common checks include:

- Unit tests for changed behavior.
- Integration or end-to-end tests for user flows.
- Lint.
- Typecheck.
- Build.
- Formatter check.
- Smoke test through CLI, browser, API call, or app preview.
- Browser screenshot or viewport inspection for frontend work.

Run the smallest meaningful checks during iteration, then run broader checks before handoff when feasible.

## Treat Failures As Work

- If a check fails because of your changes, fix it and re-run.
- If a check fails for an unrelated existing issue, verify that with evidence and state it clearly.
- If a check cannot run, record the exact command, error, and next best verification used.
- Do not use "tests were not run" as a casual caveat if a reasonable check exists.

## Commit Gate

Before a local commit:

- Review `git diff`.
- Ensure generated files are intentional.
- Ensure unrelated user changes are not staged.
- Run or document relevant checks.
- Commit only coherent completed work.

## Final Handoff

Include:

- What changed.
- Why it matters.
- Verification commands and results.
- Local commit hash if one was created.
- Known residual risks or blocked checks.
- Explicit statement: no push was performed.
