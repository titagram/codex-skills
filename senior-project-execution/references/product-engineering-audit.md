# Product And Engineering Audit

Use this before deciding what to improve.

## Classify Findings

Separate observations into:

- Product gaps: missing, unclear, or low-value flows.
- UX gaps: confusing hierarchy, unclear actions, weak states, poor copy, poor responsiveness.
- Bugs: incorrect behavior, broken flows, crashes, data loss, invalid assumptions.
- Reliability risks: unhandled errors, race conditions, weak persistence, fragile integrations.
- Maintainability risks: tangled responsibilities, duplicated logic, unclear naming, oversized files.
- Performance risks: unnecessary work, slow rendering, expensive queries, blocking operations.
- Test gaps: important behavior with no cheap way to verify it.

## Prioritize

Prefer work with high user value, high confidence, and a finishable scope. Use this order when choosing:

1. Fix broken primary workflows.
2. Remove confusing or misleading user-facing behavior.
3. Improve reliability for common paths and important edge states.
4. Add focused tests or checks for risky behavior.
5. Simplify code that blocks safe delivery.
6. Polish secondary UI only after core usefulness is solid.

Avoid broad rewrites, decorative redesigns, and unrelated cleanup. Improve the code you touch when it helps the outcome, but keep the delivery slice coherent.

## Competitive Product Judgment

Ask:

- Would a user understand what to do next?
- Does the main workflow feel complete?
- Are errors recoverable and clear?
- Does the interface look intentional and consistent?
- Is the product easier to trust after this change?

If the answer is no, treat that as engineering work, not optional polish.
