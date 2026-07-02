# Questionnaire

Ask questions after repository discovery, not before. Do not ask the user to restate facts that are visible in code or safe command output.

## Phase 1: Essential Questions

Ask 5-10 questions tailored to the repository. Prefer concise multiple-choice questions when helpful. Cover only what matters for a concrete production-readiness plan. Select from the pool below only when the topic is relevant and not already known from discovery.

Common topic pool:

- Target users and primary launch use case.
- Required launch scope versus intentionally deferred features.
- Production environment, hosting target, and release expectations.
- Business-critical workflows that must not fail.
- Data sensitivity, compliance, privacy, and retention constraints.
- Required integrations and which ones are real versus mock or future.
- Reliability expectations, uptime, support model, and recovery tolerance.
- Security posture and user roles or permission rules.
- Product quality bar for UI, onboarding, docs, and support workflows.
- Priority tradeoffs: speed to launch, robustness, UX polish, cost, or extensibility.

## Phase 2: Follow-Up Checkpoint

Phase 2 is required as a checkpoint after Phase 1. Ask only the minimal follow-ups needed, usually 1-3, when the plan would otherwise be vague or risky. If more uncertainty remains but planning can continue, convert it into explicit assumptions or open decisions instead of continuing the interview. Exceed this only when a blocker genuinely prevents a useful plan. If no follow-ups are needed, explicitly state that Phase 2 found no additional questions.

Good reasons for follow-ups include:

- Conflicting evidence in code and docs.
- Missing production target.
- Unclear data sensitivity.
- Unclear user roles or permissions.
- Unclear launch scope.
- Checks that cannot run safely.
- Major architectural ambiguity that changes implementation order.

## Question Style

- Explain briefly why the answer matters.
- Group closely related questions when it reduces friction.
- Avoid long interrogations when assumptions are acceptable.
- If the user skips a question, turn it into an explicit assumption or open decision.
- If the user provides new constraints, reflect them in task priority and acceptance criteria.

## After Answers

Before writing the plan, summarize:

- Facts verified from the repository.
- User-provided constraints.
- Assumptions being made.
- Open decisions that remain.
