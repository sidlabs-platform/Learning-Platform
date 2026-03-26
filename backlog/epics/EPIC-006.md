# Epic: Admin Reporting & Analytics

| Field       | Value                |
|-------------|----------------------|
| **Epic ID** | EPIC-006             |
| **Status**  | Ready                |
| **Owner**   | 4-develop-agent      |
| **Created** | 2026-03-26           |
| **Target**  | Sprint 3             |

## Goal / Objective

Deliver the admin reporting API — an aggregated dashboard endpoint with enrollment counts, completion rates, in-progress counts, quiz performance summaries, and filterable views — plus a CSV export capability, so administrators can measure training effectiveness and identify gaps.

## Business Value

Reporting is the mechanism by which administrators demonstrate training effectiveness (BO-2) and identify learners who have not completed courses. KPI-003 (admin progress visibility) is directly satisfied by this epic. Without reporting, admins have no operational insight into the platform's impact.

## BRD Requirements Mapped

| BRD ID        | Description                                                                             |
|---------------|-----------------------------------------------------------------------------------------|
| BRD-FR-026    | Admin dashboard: total learners, enrollments per course, completion rates, in-progress, quiz summaries |
| BRD-FR-027    | Dashboard filterable by courseId and userId                                             |
| BRD-FR-028    | CSV export of learner progress data                                                     |
| BRD-NFR-001   | Reporting endpoints respond < 2 seconds                                                 |
| BRD-NFR-013   | Reporting actions logged with requesting admin's userId                                 |
| BRD-NFR-015   | Reporting endpoint calls traceable to requesting admin in logs                          |

## Features

| Feature ID | Name                                       | Priority (P0/P1/P2) | Status  |
|------------|--------------------------------------------|----------------------|---------|
| FEAT-033   | Dashboard metrics aggregation endpoint     | P0                   | Planned |
| FEAT-034   | Per-course and per-learner filtering       | P0                   | Planned |
| FEAT-035   | CSV export of progress data                | P1                   | Planned |
| FEAT-036   | Reporting audit logging                    | P0                   | Planned |

## Acceptance Criteria

1. `GET /api/v1/reports/dashboard` (Admin only) returns all five metric categories in a single response within 2 seconds.
2. A Learner session calling `GET /api/v1/reports/dashboard` receives `403`.
3. `GET /api/v1/reports/dashboard?courseId=X` returns metrics scoped to course X only.
4. `GET /api/v1/reports/export?format=csv` returns a `text/csv` response with the defined headers.
5. Each report request creates a structured log entry containing the admin's userId.
6. Dashboard returns accurate counts: total_enrollments, completed_count, in_progress_count, completion_rate.

## Dependencies & Risks

**Dependencies:**
- EPIC-001 (ORM models, `enrollments`, `progress_records`, `quiz_attempts`, `users`, `courses`)
- EPIC-002 (require_admin dependency)
- EPIC-004 (Progress Tracking must be creating enrollment and progress data)

**Risks:**
- Aggregation query performance on larger datasets — acceptable for MVP (≤ 50 learners), but queries should use indexed columns
- CSV streaming response edge case with empty datasets — must return valid CSV with headers only

## Out of Scope

- Real-time analytics dashboards
- AI generation performance metrics
- Learner-facing progress summary (EPIC-004)

## Definition of Done

- [ ] All stories in this epic are Done
- [ ] Acceptance criteria verified
- [ ] API endpoints documented
- [ ] No critical or high-severity bugs open
- [ ] Demo-ready for stakeholder review
