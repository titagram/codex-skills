# Plan Template

Write the final plan to `<target repo>/docs/production-readiness/YYYY-MM-DD-plan.md` using the current local date. Create `docs/production-readiness/` if needed. Do not create other project files.

Use concrete repository details. Do not leave labels, blanks, or generic advice in the final plan.

## Required Structure

Use this structure. Replace every placeholder and prompt with project-specific content; do not copy instructional sentences into the final plan.

```markdown
# Production Readiness Plan - <Project Name> - <YYYY-MM-DD>

## Executive Summary

## Evidence Reviewed

- Important paths inspected, with purpose:
- Commands run, with key result:
- Commands skipped as unsafe or unavailable, with reason:
- Relevant failures, with impact:

## User Answers And Assumptions

- Confirmed facts from user answers:
- Confirmed facts from repository evidence:
- Assumptions inferred from evidence:
- Open decisions for the user:

## Roadmap

### P0 - Blocking Foundations

### P1 - Production Hardening

### P2 - Product And UX Polish

## Area Plans

### Product And UX

### Frontend

### Backend And API

### Data

### Security

### Testing And QA

### Deploy And CI

### Observability

### Performance And Scalability

### Reliability And Resilience

### Accessibility

### Privacy And Compliance

### Support And Operations

### Documentation

## Risks And Decisions

## Final Note
```

## Structure Rules

- Executive Summary: state the current readiness level, top blockers, and recommended implementation sequence.
- Roadmap: list canonical tasks in implementation order. Start with P0 blockers and foundations, then P1 production hardening, then P2 product and UX polish.
- P0: tasks required before the software can be considered launchable.
- P1: tasks that reduce operational, security, data, or reliability risk.
- P2: tasks that improve completeness, usability, supportability, and confidence.
- Area Plans: do not duplicate full task blocks. Every area must contain related roadmap task IDs plus area-specific notes/evidence, or `Not applicable` with evidence.
- Risks And Decisions: list unresolved risks, decisions needed from the user, and assumptions that should be validated before implementation.
- Final Note: state `No application code was modified.` Include the `git status --short` result when available. If unexpected command-created modifications occurred, list exact paths and state they were not staged, reverted, or deleted by this skill.

## Task Format

These are proposed future implementation steps only. During analysis, do not modify application, test, config, documentation, or asset files except this final production-readiness plan.

Every canonical roadmap task must use this shape:

```markdown
### <Priority>-<Number>: <Task Title>

- Area: <Product/UX | Frontend | Backend/API | Data | Security | Testing/QA | Deploy/CI | Observability | Performance/Scalability | Reliability/Resilience | Accessibility | Privacy/Compliance | Support/Operations | Documentation>
- Objective: <specific outcome>
- Evidence: <files, command output, or user answer that justifies the task>
- Affected paths:
  - `<path>`
  - `<path>`
- What to change: <concrete behavior, code, config, test, or doc change>
- How to change it: <implementation approach detailed enough for a later agent>
- Dependencies: <tasks or decisions that must happen first>
- Acceptance criteria:
  - <observable criterion>
  - <observable criterion>
- Verification:
  - `<command>` or manual check
  - `<command>` or manual check
```

## Path Rules

- Prefer exact paths found during discovery.
- If a path is inferred, mark it as likely and state what to verify before editing.
- Do not invent modules that conflict with the existing architecture.
- If a needed file does not exist, specify the directory where it should be created and why that matches repository conventions.

## Quality Rules

- Include product and UX tasks when the application has any user-facing surface.
- Include tests or QA checks for every high-risk behavior change.
- Include deploy, observability, and documentation work when production operation is in scope.
- Separate facts, assumptions, and open decisions.
- Keep the plan executable by another agent without a second full audit.
