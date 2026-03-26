# Epic: Frontend & User Experience

| Field       | Value                |
|-------------|----------------------|
| **Epic ID** | EPIC-007             |
| **Status**  | Ready                |
| **Owner**   | 5-ui-develop-agent   |
| **Created** | 2026-03-26           |
| **Target**  | Sprint 3–4           |

## Goal / Objective

Build the complete Jinja2-based server-rendered frontend — login page, learner dashboard and catalog, course detail and lesson viewer, quiz UI, admin course editor, AI generation form, and admin reporting dashboard — with Vanilla JS for dynamic interactions (progress auto-save, quiz submission, generation status polling), responsive layout, and XSS-safe Markdown rendering.

## Business Value

The frontend is the learner's and admin's only interface with the platform. Without it, the API-driven backend has no usable surface. This epic directly satisfies NFR-008 (≤ 2 clicks to next lesson), NFR-009 (desktop and tablet responsive), and FR-033 (AI-generated draft labels).

## BRD Requirements Mapped

| BRD ID        | Description                                                                          |
|---------------|--------------------------------------------------------------------------------------|
| BRD-FR-033    | Admin UI labels AI-generated sections as "AI-generated draft"                       |
| BRD-FR-035    | Admin UI shows AI generation error and retry button                                  |
| BRD-NFR-008   | Learner reaches next lesson within 2 clicks from dashboard                           |
| BRD-NFR-009   | UI responsive on desktop (≥ 1280 px) and tablet (768–1279 px)                       |
| BRD-NFR-006   | Markdown rendered safely (XSS-sanitised output from server baked in)                |

## Features

| Feature ID | Name                                       | Priority (P0/P1/P2) | Status  |
|------------|--------------------------------------------|----------------------|---------|
| FEAT-037   | Base HTML template and CSS design system   | P0                   | Planned |
| FEAT-038   | Authentication pages (login)               | P0                   | Planned |
| FEAT-039   | Learner dashboard and course catalog       | P0                   | Planned |
| FEAT-040   | Course detail and lesson viewer            | P0                   | Planned |
| FEAT-041   | Quiz UI                                    | P0                   | Planned |
| FEAT-042   | Admin course management UI                 | P0                   | Planned |
| FEAT-043   | Admin AI generation form + status polling  | P0                   | Planned |
| FEAT-044   | Admin reporting dashboard UI               | P0                   | Planned |
| FEAT-045   | Frontend page router (Jinja2 routes)       | P0                   | Planned |
| FEAT-046   | Vanilla JS modules (progress, quiz, AI, editor) | P0             | Planned |

## Acceptance Criteria

1. Learner can reach their next lesson from the dashboard in ≤ 2 clicks.
2. All pages render correctly on desktop (1280 px) and tablet (768 px) viewports.
3. Lesson Markdown content renders safely — no script execution on injected payloads.
4. Admin AI generation form shows a spinner during generation, displays error with retry button on failure, and shows success with link to draft course on completion.
5. Admin course editor shows "AI-generated draft" badge on AI-sourced sections.
6. Quiz form shows score summary (correct/total/percentage/pass-fail) after submission.
7. Completing a lesson via the "Mark Complete" button immediately updates the progress bar without page reload.
8. Login page redirects to role-appropriate dashboard on success.

## Dependencies & Risks

**Dependencies:**
- EPIC-002 (Auth — login/logout endpoints and JWT cookie)
- EPIC-003 (Course Management — catalog, course detail, module/lesson APIs)
- EPIC-004 (Progress Tracking — enrollment, progress, quiz APIs)
- EPIC-005 (AI Generation — generation trigger and status polling APIs)
- EPIC-006 (Reporting — dashboard and CSV export APIs)

**Risks:**
- Vanilla JS complexity for polling loops and dynamic DOM updates — mitigate with clear module structure
- Jinja2 template context scope errors — mitigate with thorough integration testing
- Responsive layout breakage at edge viewports — mitigate with explicit CSS breakpoints

## Out of Scope

- React, Vue, Angular, or any JS framework
- Native mobile applications
- Social features (comments, likes, forums)
- Client-side Markdown sanitisation (server-side bleach is the defence)

## Definition of Done

- [ ] All stories in this epic are Done
- [ ] Acceptance criteria verified
- [ ] API endpoints documented
- [ ] No critical or high-severity bugs open
- [ ] Demo-ready for stakeholder review
