# Production Readiness Audit

Evaluate whether the repository can become a finished production software product. Tie every finding to repository evidence when possible.

## Audit Rules

- Read-only analysis only; identify gaps, do not implement fixes, scaffold code, rewrite files, or change config.
- Every finding must include repository evidence, command evidence, user answer, or be explicitly marked as an assumption/unknown.
- Prefer concrete gaps over checklist completion.
- Every finding should include affected paths or explain why no path is available.

## Finding Format

- Category
- Severity
- Launch risk
- Evidence
- Gap
- Impact
- Affected paths
- Recommended task
- Dependencies
- Acceptance criteria

## Prioritization

Rank gaps by:

- Launch risk: defects, missing flows, security holes, data loss, unavailable deploy path.
- User value: gaps that block or degrade primary workflows.
- Implementation dependency: foundations that unblock later work.
- Confidence: observed evidence beats speculation.
- Cost: prefer high-leverage fixes before polish with low impact.

## Product And UX

Check:

- Primary user journeys are complete from entry to success.
- Onboarding, auth, permissions, settings, billing, admin, support, import/export, and notification flows exist when the product implies them.
- Empty, loading, error, success, offline, permission-denied, and edge states are handled.
- Forms validate clearly and preserve user input on errors.
- Navigation, information hierarchy, copy, and feedback are understandable.
- Responsive behavior and accessibility basics are covered for user-facing UI, including keyboard navigation, focus states, semantic structure, contrast, screen reader behavior, and critical-flow accessibility testing.
- The product has a coherent launch scope rather than scattered unfinished surfaces.

## Frontend

Check:

- Routing and page boundaries match user workflows.
- Components have clear responsibilities and avoid tangled state.
- API calls handle loading, success, empty, error, retry, auth expiry, and validation errors.
- Client-side validation mirrors server constraints where relevant.
- State management is understandable and scoped.
- Performance risks are visible: large bundles, unnecessary client rendering, missing pagination, expensive re-renders, unoptimized media.
- Tests cover critical interactions and regression-prone components.

## Backend And API

Check:

- Domain boundaries, service layers, controllers, handlers, jobs, and API contracts are coherent.
- Authentication and authorization are enforced server-side.
- Input validation, error handling, status codes, and response shapes are consistent.
- Data writes are transactional or idempotent where needed.
- Background jobs, queues, webhooks, and scheduled tasks are retryable and observable.
- Rate limits, abuse cases, and external integration failures are considered.
- API tests cover critical success and failure cases.

## Data

Check:

- Schema, migrations, indexes, constraints, and relationships match product workflows.
- Sensitive data has clear handling, retention, privacy, consent, auditability, and access rules.
- Backups, restore expectations, seed strategy, and data lifecycle are defined where production requires them.
- Reports, exports, analytics, or audit logs have reliable sources of truth.
- Compliance and legal data obligations are visible where relevant, including retention, deletion, residency, regulatory, and customer export requirements.

## Reliability And Production Behavior

Check:

- Availability expectations, health checks, and critical failure modes are defined.
- Timeout, retry, circuit-breaker, idempotency, and graceful degradation behavior is explicit for external services and slow operations.
- Capacity, scaling, pagination, queue depth, and resource assumptions are realistic for launch.
- Backup restore, rollback, and migration recovery paths are verified or clearly untested.
- Incident response, degraded-mode behavior, ownership, escalation, and user-facing status expectations are documented where production risk warrants them.

## Security

Check:

- Secrets are not committed and configuration uses environment variables or approved secret stores.
- Dependencies, package health, update strategy, license compatibility, framework versions, and unsupported runtimes do not show obvious risk.
- Auth, authorization, CSRF, CORS, XSS, SQL injection, SSRF, file upload, and webhook verification are addressed where relevant.
- Logs avoid leaking secrets and sensitive personal data.
- Secure defaults exist for production config.
- Consent, cookies/tracking, terms/privacy policy, licensing, auditability, and regulatory obligations are addressed where the product or jurisdiction implies them.

## Testing And QA

Check:

- Unit, integration, end-to-end, smoke, accessibility, and performance tests exist where the risk justifies them.
- Tests cover primary workflows, auth, permissions, validation, errors, and regressions.
- CI runs meaningful checks.
- Manual release checks are documented for flows that cannot be automated yet.

## Delivery And Operations

Check:

- Build, deploy, environment, rollback, and release procedures are clear.
- CI/CD exists or has a realistic path.
- Production config, env samples, Docker/container setup, infrastructure scripts, supported runtimes, or hosting settings are present where needed.
- Observability covers logs, metrics, traces, alerts, error reporting, health checks, and runbooks.
- Documentation explains local setup, production setup, troubleshooting, operational ownership, dependency maintenance, legal/compliance ownership, and release signoff.
