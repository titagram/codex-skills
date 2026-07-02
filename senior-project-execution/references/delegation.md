# Delegation

Use subagents to increase coverage only when tasks are independent enough to verify and integrate cleanly.

## Good Delegation Targets

- Repository orientation or architecture mapping.
- Independent bug investigation.
- Test coverage suggestions for a focused module.
- UX review of a specific screen or flow.
- Implementation of a small isolated component, function, or test file.
- Regression sweep after changes.

## Poor Delegation Targets

- Final product judgment.
- Broad rewrites without clear boundaries.
- Work requiring secrets, production access, or user credentials.
- Changes that overlap heavily with current edits.
- Tasks where you cannot inspect the result.

## Prompt Shape

Give each subagent:

- The exact goal.
- The relevant files or commands to inspect.
- Constraints, including no push and no destructive git operations.
- Expected output format.
- Verification expectations.

Do not leak conclusions you want validated unless the task explicitly needs them. Prefer raw artifacts and neutral instructions.

## Integration

After a subagent returns:

- Inspect its reasoning and changed files.
- Review diffs yourself.
- Resolve conflicts and remove weak or speculative work.
- Run relevant checks.
- Keep final responsibility for whether the result ships.

If the result is incomplete, either fix it yourself, send a narrower follow-up, or discard it.
