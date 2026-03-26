# Epic: Authentication & Authorisation

| Field       | Value                |
|-------------|----------------------|
| **Epic ID** | EPIC-002             |
| **Status**  | Ready                |
| **Owner**   | 4-develop-agent      |
| **Created** | 2026-03-26           |
| **Target**  | Sprint 1             |

## Goal / Objective

Implement the complete authentication and role-based access control (RBAC) system — email/password sign-in, JWT issuance via HTTP-only cookies, role enforcement (Learner / Admin), and per-user data isolation — so that all subsequent service endpoints can be secured with a `Depends()` call.

## Business Value

Authentication and RBAC are the security foundation of the platform. Without them, all course data, learner progress, and admin capabilities are exposed. This epic directly enables the BRD's two-role model and ensures learner data privacy (BRD-FR-004).

## BRD Requirements Mapped

| BRD ID        | Description                                                                                |
|---------------|--------------------------------------------------------------------------------------------|
| BRD-FR-001    | Users sign in with email/password and receive an authenticated session                      |
| BRD-FR-002    | Exactly two roles: `learner` and `admin`                                                   |
| BRD-FR-003    | Admin-only endpoints restricted from Learner sessions (403)                                |
| BRD-FR-004    | Learners can only access their own progress data                                           |
| BRD-NFR-004   | RBAC enforced on every endpoint; returns 401 without session, 403 for wrong role           |
| BRD-NFR-005   | API keys and secrets never hardcoded, logged, or returned in responses                     |
| BRD-NFR-013   | Authentication events (sign-in, sign-out, failed attempts) are logged                     |

## Features

| Feature ID | Name                              | Priority (P0/P1/P2) | Status  |
|------------|-----------------------------------|----------------------|---------|
| FEAT-007   | Email/password sign-in endpoint   | P0                   | Planned |
| FEAT-008   | JWT issuance with HTTP-only cookie| P0                   | Planned |
| FEAT-009   | RBAC dependency injection functions | P0                 | Planned |
| FEAT-010   | Sign-out endpoint (cookie clear)  | P0                   | Planned |
| FEAT-011   | Auth event logging                | P0                   | Planned |

## Acceptance Criteria

1. `POST /api/v1/auth/login` with valid credentials returns `200` and sets an HTTP-only `SameSite=Strict` JWT cookie.
2. `POST /api/v1/auth/login` with invalid credentials returns `401` with an error message; no cookie is set.
3. A Learner session calling any admin-only endpoint returns `403 Forbidden`.
4. An unauthenticated request to any protected endpoint returns `401 Unauthorized`.
5. A Learner cannot retrieve another Learner's progress records (returns `403`).
6. Auth events (successful login, logout, failed login) appear in structured log entries.
7. JWT tokens expire after the configured TTL (default: 8 hours).

## Dependencies & Risks

**Dependencies:**
- EPIC-001 (Data Layer — `users` table and `get_db()` dependency must exist)

**Risks:**
- JWT secret rotation will invalidate all active sessions — acceptable for MVP
- HTTP-only cookie CSRF risk in non-browser contexts — mitigated by `SameSite=Strict`

## Out of Scope

- SSO / OAuth / identity federation
- Password reset flows
- Multi-factor authentication
- User self-registration (handled by seed / admin-only endpoint)

## Definition of Done

- [ ] All stories in this epic are Done
- [ ] Acceptance criteria verified
- [ ] API endpoints documented
- [ ] No critical or high-severity bugs open
- [ ] Demo-ready for stakeholder review
