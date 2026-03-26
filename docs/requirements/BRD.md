# Business Requirements Document (BRD)

| Field       | Value                                                     |
|-------------|-----------------------------------------------------------|
| **Title**   | Learning Platform MVP — Business Requirements Document    |
| **Version** | 1.0                                                       |
| **Date**    | 2026-03-26                                                |
| **Author**  | 1-requirement-agent                                       |
| **Status**  | Draft                                                     |

---

## 1. Executive Summary

### 1.1 Project Overview

The Learning Platform MVP is an internal training application that enables **Learners** to enroll in and complete structured GitHub-focused courses, while **Admins** create, manage, and publish course content — accelerated by AI-assisted generation through the **GitHub Models API** (GPT-4o). The platform tracks learner progress at the lesson, module, and course level, and provides admins with a reporting dashboard for enrollment and completion metrics.

The system is built on **Python 3.11 / FastAPI** with a **SQLite** database and a **Vanilla HTML/CSS/JS + Jinja2** frontend. It ships with three seeded starter courses (**GitHub Foundations**, **GitHub Advanced Security**, and **GitHub Actions**) and a full draft-review-publish governance workflow for all AI-generated content.

The primary business problem the platform solves is the high cost and effort of manually authoring GitHub training content, combined with the lack of a simple mechanism to track whether staff have completed that training.

### 1.2 Business Objectives

- **BO-1**: Provide a simple, low-friction training experience focused on GitHub topics, enabling teams to onboard learners into GitHub learning journeys without a full-featured LMS.
- **BO-2**: Enable administrators to measure learner progress and course completion to demonstrate training effectiveness and identify gaps.
- **BO-3**: Reduce content authoring time and effort by using the GitHub Models API (GPT-4o) to generate draft course outlines, lesson content, quiz questions, and summaries.
- **BO-4**: Validate organisational interest in an AI-assisted learning platform before committing resources to a full-featured LMS investment.

### 1.3 Success Metrics / KPIs

| Metric ID | Metric                                          | Target                                              | Measurement Method                                     |
|-----------|-------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------|
| KPI-001   | Minimum published courses at launch             | ≥ 3 courses (GitHub Foundations, GHAS, Actions)     | Count of courses with status = `published` in database |
| KPI-002   | End-to-end learner course completion            | Learner can enroll in and fully complete ≥ 1 course | Manual QA test + ProgressRecord completion flag        |
| KPI-003   | Admin progress visibility                       | Admin can view per-user and per-course progress      | Dashboard displays enrollment count and % complete     |
| KPI-004   | AI-assisted draft generation                    | GitHub Models generates reviewable draft in < 60 s  | ContentGenerationRequest latency log                   |
| KPI-005   | Platform availability during AI service outage  | Published courses remain accessible when AI is down | Functional test with AI service mocked as unavailable  |

---

## 2. Background & Context

GitHub-focused training is a recurring need for development teams adopting or deepening their use of GitHub products. Currently, content is authored manually in documents or slide decks, distributed inconsistently, and completion is tracked (if at all) via spreadsheets or email. There is no central record of who has completed which training, no standard lesson format, and no mechanism for quickly updating content as GitHub products evolve.

The GitHub Models API (GPT-4o) presents an opportunity to dramatically accelerate the initial content authoring cycle by generating structured course drafts — outlines, lesson markdown, quiz questions, and summaries — from a simple admin prompt. Admins retain full editorial control through a mandatory review-and-publish workflow before any AI-generated content becomes visible to learners.

This MVP is scoped to a single-organisation deployment and intentionally avoids the overhead of enterprise LMS integrations, payment systems, certificates, and social features. The goal is to ship a working, testable platform quickly, measure adoption and completion rates against the three starter courses, and use those signals to decide whether to invest in a broader LMS.

---

## 3. Stakeholders

| Name                      | Role                                        | Interest                                                                           | Influence |
|---------------------------|---------------------------------------------|------------------------------------------------------------------------------------|-----------|
| Platform Admin / L&D Lead | Internal administrator, primary admin user  | Needs an efficient way to create, manage, and publish GitHub courses; track completion | High      |
| Learner / Developer       | Developer or engineer consuming the courses | Needs clear, easy-to-navigate course content and progress visibility               | High      |
| Engineering / DevOps Lead | Technical sponsor                           | Concerned with reliability, security, maintainability, and AI integration quality  | High      |
| GitHub Models / API Owner | External service provider                   | Ensures API terms are respected; rate limits and quota are not exceeded             | Medium    |
| Content Author (future)   | Potential future role, not in MVP           | Would want a separate authoring workflow distinct from admin governance             | Low       |

---

## 4. Scope

### 4.1 In-Scope

- **Authentication and authorisation** with role-based access control (Learner and Admin roles).
- **Course catalog** displaying published courses with title, description, difficulty, duration, and status.
- **Course structure**: hierarchical Course → Module → Lesson + QuizQuestion model.
- **Lesson types**: Markdown/rich text, links, and embedded media.
- **Learner progress tracking** at lesson, module, and course level, including last-accessed lesson resume.
- **Quiz support** with multiple-choice questions, score recording, pass/fail display.
- **Admin dashboard** for viewing enrollments, completion rates, module-level progress, and quiz performance.
- **Admin enrollment management**: assigning courses to learners; optional self-enrollment for published courses.
- **AI-assisted course generation** using the GitHub Models API (GPT-4o): course outline, lesson drafts, quiz questions, key takeaways.
- **Draft-review-publish governance workflow**: all AI-generated content starts as draft; admin must review and publish.
- **Prompt metadata storage**: prompt text, model used, timestamp, requester, and generation status stored for audit.
- **Content regeneration**: admin can regenerate an individual section (module, lesson, quiz) without regenerating the whole course.
- **Basic course search and filter** by topic and difficulty in the catalog.
- **Starter seeded content** for three courses at launch: **GitHub Foundations**, **GitHub Advanced Security**, **GitHub Actions**.
- **Draft vs. published course versioning** (simple status flag; previously published content preserved when a draft is edited).
- **CSV export** of basic progress data (Should-Have for MVP; see release slice).
- **MCP-ready architecture**: AI generation service designed as a pluggable module with separated prompt orchestration, model invocation, content persistence, and review workflow — so MCP tool exposure can be added later without refactoring.

### 4.2 Out-of-Scope

- Payments or subscription management.
- Certificates with advanced verification or SCORM/xAPI compliance.
- Social features: comments, likes, forums, peer reviews.
- Native mobile applications (iOS / Android).
- Advanced adaptive learning or AI-driven learner recommendations.
- Multi-tenant / multi-organisation support (single-organisation deployment only).
- Deep integrations with enterprise HR or LMS tools (Workday, SAP SuccessFactors, etc.).
- A separate Content Author role distinct from Admin.
- Full MCP tool ecosystem integration (architecture must remain MCP-ready, but full MCP server is a future release item).
- SSO / identity federation beyond basic auth (future enhancement).
- Learning paths that chain multiple courses.
- Automated notifications and reminders to learners.

### 4.3 Assumptions

- The MVP is deployed for a single organisation or shared environment; multi-tenancy is not required.
- Only Admins can create, edit, and publish courses; Learners consume published content only.
- AI generation is **assistive, not autonomous** — no AI-generated content is ever auto-published.
- The team building and administering the platform has access to a valid GitHub Models API key (GPT-4o access).
- The environment variable `GITHUB_MODELS_API_KEY` is available at runtime; the endpoint is configured via `GITHUB_MODELS_ENDPOINT`.
- The SQLite database is adequate for MVP scale (single file, no high-concurrency requirement).
- Learner authentication is handled by the platform's own sign-in mechanism; SSO/OAuth with a corporate identity provider is a future enhancement.
- Certificates are out of scope for the MVP, even in lightweight form.
- Quiz passing may be configured as either mandatory or informational by the admin per course.
- AI generation may take longer than typical API calls; async generation with a polling/status pattern is acceptable.

### 4.4 Constraints

- **Tech stack is fixed for MVP**: Python 3.11+, FastAPI, Pydantic v2, SQLite, Jinja2 + Vanilla JS, pytest.
- **AI backend is fixed**: GitHub Models API (GPT-4o) only; no other model provider in MVP.
- **No framework changes**: no React, Vue, Angular, or other frontend frameworks.
- **Secrets never hardcoded**: all credentials and configuration loaded from environment variables via `pydantic-settings`.
- **MCP**: full MCP server is out of scope for MVP; the AI generation module must be designed to be MCP-compatible without requiring a full MCP server.
- **Performance**: non-AI API responses must be < 2 seconds; AI generation may be asynchronous.
- **Security**: RBAC enforced on all endpoints; XSS prevention required for all rendered Markdown content; CORS scoped appropriately.

### 4.5 Dependencies

- **GitHub Models API** (GPT-4o): availability, rate limits, and quota directly affect the AI generation feature. If unavailable, published course consumption must continue unaffected.
- **Python 3.11+** runtime environment.
- **SQLite** file system access for the database.
- **FastAPI / Uvicorn** ASGI server.
- **Pydantic v2** for data validation and settings management.
- **pytest + httpx AsyncClient + respx/unittest.mock** for the test suite.

---

## 5. Use Cases

| Use Case ID | Name                                    | Description                                                                                                                                                      | Priority    | Actors          |
|-------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|-----------------|
| UC-001      | Learner Sign-In                         | Learner authenticates with email/password credentials and receives a session. The system enforces the Learner role, granting access only to catalog and own progress. | Must-Have   | Learner         |
| UC-002      | View Course Catalog                     | Learner browses the list of published courses, sees title, description, difficulty, and duration, and filters by topic or difficulty.                             | Must-Have   | Learner         |
| UC-003      | Enroll in a Course                      | Learner self-enrolls in a published course, or is enrolled by an Admin. Enrollment status is set to `not_started`.                                               | Must-Have   | Learner, Admin  |
| UC-004      | Complete a Lesson                       | Learner opens a course, navigates to a lesson, reads/views content, and marks it complete. Progress is auto-saved.                                               | Must-Have   | Learner         |
| UC-005      | Resume a Course                         | Learner returns to a course already in progress and is taken directly to the last-accessed lesson.                                                               | Must-Have   | Learner         |
| UC-006      | Take a Quiz                             | Learner answers multiple-choice quiz questions for a module, submits answers, and sees score and pass/fail result.                                               | Must-Have   | Learner         |
| UC-007      | View Own Progress                       | Learner views overall completion percentage for each enrolled course and which modules/lessons are done.                                                          | Must-Have   | Learner         |
| UC-008      | Admin Sign-In                           | Admin authenticates and receives a session with Admin-role access, unlocking authoring, publishing, enrollment, and reporting features.                          | Must-Have   | Admin           |
| UC-009      | Create a Course Manually                | Admin creates a new course by entering title, description, difficulty, duration, audience, objectives, and tags; adds modules and lessons manually.              | Must-Have   | Admin           |
| UC-010      | Generate Course Draft with AI           | Admin inputs topic, audience, objectives, difficulty, desired module count, and preferred tone; the system calls GitHub Models and saves a draft with all generated sections. | Must-Have   | Admin           |
| UC-011      | Review and Edit AI-Generated Content    | Admin opens a generated draft, reads generated content section by section, edits as needed, and marks sections as reviewed. Draft remains unpublished.           | Must-Have   | Admin           |
| UC-012      | Publish a Course                        | Admin publishes a reviewed draft course, making it visible in the learner catalog.                                                                               | Must-Have   | Admin           |
| UC-013      | Regenerate a Section                    | Admin selects a single module, lesson, or quiz section and requests a regeneration from GitHub Models without regenerating the whole course.                     | Should-Have | Admin           |
| UC-014      | Enroll Learners in a Course             | Admin selects one or more learners and assigns them to a course; enrollment records are created.                                                                 | Must-Have   | Admin           |
| UC-015      | View Admin Reporting Dashboard          | Admin opens the reporting dashboard, sees total learners, enrollments per course, completion rates, in-progress counts, and quiz score summaries.                | Must-Have   | Admin           |
| UC-016      | Filter Reporting Data                   | Admin filters the dashboard view by course, learner, or enrollment status.                                                                                       | Must-Have   | Admin           |
| UC-017      | Export Progress Data to CSV             | Admin exports filtered enrollment and progress data as a CSV file.                                                                                               | Should-Have | Admin           |
| UC-018      | Unpublish a Course                      | Admin unpublishes a published course so it is no longer visible to learners; existing progress records are retained.                                             | Must-Have   | Admin           |
| UC-019      | View AI Generation Audit Log            | Admin views a list of past ContentGenerationRequests, including prompt, model, timestamp, requester, and status.                                                 | Should-Have | Admin           |
| UC-020      | Access Starter Course (Seeded Content)  | Learner accesses one of the three seeded courses (GitHub Foundations, GHAS, GitHub Actions) from the catalog on first launch.                                   | Must-Have   | Learner, Admin  |

---

## 6. Functional Requirements

### 6.1 Authentication and Authorisation

| Req ID     | Description                                                                                                                      | Priority   | Acceptance Criteria                                                                                                                                              |
|------------|----------------------------------------------------------------------------------------------------------------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-001 | The system shall allow users to sign in with email and password credentials and receive an authenticated session.                | Must Have  | Given valid credentials, a session token is returned and the user can access protected routes. Given invalid credentials, a 401 response with an error message is returned. |
| BRD-FR-002 | The system shall support exactly two roles: `Learner` and `Admin`.                                                               | Must Have  | Each User record has a role field that is either `learner` or `admin`. Attempting to set any other role value fails validation.                                   |
| BRD-FR-003 | The system shall restrict course creation, editing, publishing, enrollment management, and reporting endpoints to Admin role only. | Must Have  | A request from a Learner session to any admin-only endpoint returns 403. A request from an Admin session succeeds with the appropriate response.                  |
| BRD-FR-004 | The system shall restrict a Learner's access to their own progress data only; a Learner cannot view another Learner's progress.  | Must Have  | A Learner requesting progress records for a different userId receives 403. A Learner requesting their own records receives 200 with their data.                    |

### 6.2 Course Catalog

| Req ID     | Description                                                                                                                         | Priority   | Acceptance Criteria                                                                                                                                    |
|------------|-------------------------------------------------------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-005 | The system shall display a catalog of courses whose status is `published`, showing title, description, difficulty, estimated duration, and tags. | Must Have  | GET `/api/v1/courses` returns only courses with `status=published`, each with title, description, difficulty, estimatedDuration, and tags fields.       |
| BRD-FR-006 | The system shall support filtering the course catalog by topic (tag) and difficulty level.                                          | Must Have  | GET `/api/v1/courses?difficulty=beginner` returns only beginner courses. GET `/api/v1/courses?tag=github-actions` returns only courses tagged accordingly. |
| BRD-FR-007 | Admins shall be able to publish a course (transition status from `draft` to `published`).                                           | Must Have  | PATCH `/api/v1/courses/{id}/publish` by an Admin changes status to `published` and the course appears in the learner catalog. A Learner session calling this endpoint returns 403. |
| BRD-FR-008 | Admins shall be able to unpublish a course (transition status from `published` to `draft`).                                         | Must Have  | PATCH `/api/v1/courses/{id}/unpublish` by an Admin changes status to `draft`. The course no longer appears in GET `/api/v1/courses` for Learners. Existing progress records are preserved. |

### 6.3 Course Structure

| Req ID     | Description                                                                                                                                   | Priority   | Acceptance Criteria                                                                                                                                              |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-009 | The system shall support a four-level content hierarchy: Course → Module → Lesson → QuizQuestion.                                             | Must Have  | A course can be retrieved with its full nested structure: modules array, each with a lessons array and a quizQuestions array.                                     |
| BRD-FR-010 | Each Course record shall store: title, description, status, difficulty, estimatedDuration, targetAudience, learningObjectives, and tags.      | Must Have  | POST `/api/v1/courses` with all required fields returns a 201 with a course object containing all specified attributes. Missing required fields return 422.       |
| BRD-FR-011 | Each Lesson shall support Markdown content stored in a `markdownContent` field with an `estimatedMinutes` attribute.                          | Must Have  | A lesson returned from the API contains a `markdownContent` string and an `estimatedMinutes` integer. Markdown is rendered safely in the frontend (XSS-sanitized). |
| BRD-FR-012 | Each Module may include one or more QuizQuestions with fields: question, options[], correctAnswer, and explanation.                           | Must Have  | A module returned from the API includes a `quizQuestions` array. Each item has `question`, `options` (≥ 2 items), `correctAnswer`, and `explanation` fields.     |
| BRD-FR-013 | Modules and Lessons shall be ordered by a `sortOrder` integer, allowing admins to reorder content.                                            | Should Have | Modules within a course are returned ordered by `sortOrder` ascending. Updating `sortOrder` on a module changes its position in the list.                        |

### 6.4 Enrollment

| Req ID     | Description                                                                                                                   | Priority   | Acceptance Criteria                                                                                                                                    |
|------------|-------------------------------------------------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-014 | Admins shall be able to enroll one or more Learners in a course, creating Enrollment records with status `not_started`.       | Must Have  | POST `/api/v1/enrollments` by Admin with userId and courseId creates an Enrollment with `status=not_started`. Duplicate enrollment for the same user/course returns 409. |
| BRD-FR-015 | The system shall support optional self-enrollment: a Learner may enroll themselves in any published course.                   | Should Have | POST `/api/v1/enrollments` by a Learner session with their own userId and a published courseId creates an Enrollment. Attempting to enroll in an unpublished course returns 404. |
| BRD-FR-016 | Enrollment status shall progress through three states: `not_started` → `in_progress` → `completed`.                          | Must Have  | When a Learner completes the first lesson, enrollment status becomes `in_progress`. When all required modules and quizzes are complete, status becomes `completed`. |

### 6.5 Learner Progress Tracking

| Req ID     | Description                                                                                                                                  | Priority   | Acceptance Criteria                                                                                                                                                 |
|------------|----------------------------------------------------------------------------------------------------------------------------------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-017 | The system shall persist a ProgressRecord for each Learner/Lesson combination, recording `completed`, `completedAt`, and `lastViewedAt`.     | Must Have  | When a Learner views a lesson, a ProgressRecord is created or updated with `lastViewedAt`. When marked complete, `completed=true` and `completedAt` are set.         |
| BRD-FR-018 | The system shall record the last-accessed lesson for each Learner/Enrollment and support resuming from that lesson.                          | Must Have  | GET `/api/v1/enrollments/{id}/resume` returns the lessonId of the last-accessed lesson. The frontend navigates the Learner directly to that lesson.                  |
| BRD-FR-019 | The system shall calculate and return a course completion percentage for each Enrollment, based on completed lessons vs. total required lessons. | Must Have  | GET `/api/v1/enrollments/{id}` returns a `completionPercentage` field (0–100). After completing all lessons, value is 100.                                           |
| BRD-FR-020 | The system shall automatically mark an Enrollment as `completed` when all required lessons and any mandatory quizzes are finished.            | Must Have  | When the last required lesson and quiz are marked complete, the Enrollment status transitions to `completed` and `completedAt` is recorded.                          |
| BRD-FR-021 | Progress shall not be lost if a Learner refreshes the page or navigates away mid-lesson.                                                      | Must Have  | ProgressRecord `lastViewedAt` is written on lesson open (not only on explicit save). After a page refresh, the Learner's progress state is unchanged.               |

### 6.6 Quizzes and Assessments

| Req ID     | Description                                                                                                              | Priority   | Acceptance Criteria                                                                                                                                          |
|------------|--------------------------------------------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-022 | The system shall support multiple-choice quiz questions, each with 2–5 answer options, one correct answer, and an explanation. | Must Have  | A QuizQuestion with fewer than 2 options or no correctAnswer returns 422 on creation. A valid question is stored and retrieved correctly.                     |
| BRD-FR-023 | The system shall record each QuizAttempt: userId, quizQuestionId, selectedAnswer, isCorrect, and attemptedAt.            | Must Have  | POST `/api/v1/quiz-attempts` creates a QuizAttempt record. `isCorrect` is computed server-side by comparing selectedAnswer to correctAnswer.                  |
| BRD-FR-024 | The system shall return a score summary (number correct, total questions, percentage, pass/fail) after quiz submission.   | Must Have  | POST `/api/v1/enrollments/{id}/quiz-submit` returns `{ correct, total, percentage, passed }`. `passed` reflects whether the score meets the configured passing threshold. |
| BRD-FR-025 | Admins shall be able to configure a passing score threshold per quiz, or mark the quiz as informational only (no pass/fail). | Must Have  | A Module has a `quizPassingScore` field (0–100) and an `isQuizInformational` boolean. When `isQuizInformational=true`, quiz result does not block course completion. |

### 6.7 Admin Reporting

| Req ID     | Description                                                                                                                                    | Priority   | Acceptance Criteria                                                                                                                                          |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-026 | The system shall provide an admin dashboard endpoint returning: total learner count, enrollments per course, completion rates, in-progress counts, and quiz score summaries. | Must Have  | GET `/api/v1/reports/dashboard` (Admin only) returns all five metrics in a single response. A Learner session returns 403.                                    |
| BRD-FR-027 | The dashboard shall support filtering by courseId and userId.                                                                                   | Must Have  | GET `/api/v1/reports/dashboard?courseId=X` returns metrics scoped to course X. GET with `userId=Y` returns metrics scoped to that learner.                   |
| BRD-FR-028 | The system shall support exporting learner progress data as a CSV file.                                                                         | Should Have | GET `/api/v1/reports/export?format=csv` (Admin only) returns a `text/csv` response with headers: userId, userName, courseId, courseTitle, enrollmentStatus, completionPercentage, lastActivity. |

### 6.8 AI-Assisted Course Generation

| Req ID     | Description                                                                                                                                                                                        | Priority   | Acceptance Criteria                                                                                                                                                                         |
|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-029 | The system shall accept an admin generation request with fields: topic, targetAudience, learningObjectives[], difficulty, desiredModuleCount, and preferredTone.                                   | Must Have  | POST `/api/v1/ai/generate-course` with all required fields returns 202 Accepted with a `generationRequestId`. Missing required fields return 422.                                           |
| BRD-FR-030 | The system shall call the GitHub Models API (GPT-4o) and generate: course title suggestions, course description, module outline, lesson draft content, quiz questions and answers, and key takeaways. | Must Have  | On successful generation, a ContentGenerationArtifact is created containing all six content types in the defined JSON schema (see Section 8.5). The artifact status is `draft`.             |
| BRD-FR-031 | All AI-generated content shall be saved with status `draft` and must never be auto-published.                                                                                                      | Must Have  | After generation completes, querying the resulting course returns `status=draft`. No generated content is visible in the learner catalog without an explicit admin publish action.           |
| BRD-FR-032 | The system shall store generation metadata for every request: promptText, modelUsed, requesterId, generationStatus, createdAt, and resolvedAt.                                                     | Must Have  | A ContentGenerationRequest record is created on generation trigger. After completion, the record contains all metadata fields including modelUsed and completedAt timestamp.                 |
| BRD-FR-033 | The system shall label generated content as "AI-generated draft" in the admin UI until the admin approves/publishes it.                                                                            | Must Have  | Admin course editor displays an "AI-generated draft" badge on any section derived from a ContentGenerationArtifact that has not yet been approved.                                          |
| BRD-FR-034 | Admins shall be able to regenerate a single module, lesson, or quiz section without triggering regeneration of the entire course.                                                                  | Should Have | POST `/api/v1/ai/regenerate-section` with `sectionType` and `sectionId` triggers a new ContentGenerationRequest scoped to that section only. Other sections are unaffected.                 |
| BRD-FR-035 | AI generation failures shall not affect learner access to already-published courses and shall return a clear, retryable error state to the admin.                                                  | Must Have  | When GitHub Models API returns a non-2xx response or times out, the ContentGenerationRequest status is set to `failed` with an error message. The admin UI displays the error and a retry button. Published courses remain accessible. |
| BRD-FR-036 | The system shall support a predefined library of reusable prompt templates for: generate course outline, generate lesson content, generate quiz questions, summarise module, and rewrite for different skill level. | Must Have  | Five prompt template records exist in the system. Each template is used by the corresponding generation action. Admins can view which template was used via the generation audit log.       |
| BRD-FR-037 | Rendered lesson content (including AI-generated Markdown) shall be sanitised server-side to prevent XSS injection.                                                                                 | Must Have  | Lesson content containing `<script>` tags or javascript: URLs is stripped before being served. A test with malicious Markdown input confirms no script execution occurs in the rendered page. |

### 6.9 Course Versioning and Governance

| Req ID     | Description                                                                                                                     | Priority   | Acceptance Criteria                                                                                                                              |
|------------|---------------------------------------------------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-038 | The system shall support two course states: `draft` and `published`. Editing a published course transitions it to a new draft without removing the published version from the learner catalog. | Should Have | When an Admin edits a published course, the system creates a new draft version. Learners continue to see the previously published version until the draft is re-published. |
| BRD-FR-039 | The system shall indicate which content sections were AI-generated and which were manually authored.                             | Should Have | Each lesson and module record has an `isAiGenerated` boolean. The admin editor displays a visual indicator for AI-generated sections.            |
| BRD-FR-040 | The system should retain a simple revision history visible to admins for audit purposes.                                        | Nice to Have | GET `/api/v1/courses/{id}/revisions` (Admin only) returns a list of past versions with timestamp and author.                                    |

### 6.10 Starter Seeded Content

| Req ID     | Description                                                                                                                                                                                | Priority   | Acceptance Criteria                                                                                                                             |
|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| BRD-FR-041 | The system shall ship with a seeded **GitHub Foundations** course containing 5 modules: (1) Introduction to Git and GitHub, (2) Repositories, Branches, and Commits, (3) Pull Requests and Code Reviews, (4) Issues and Project Basics, (5) Collaboration Best Practices. | Must Have  | On first launch (or seed migration), a published GitHub Foundations course with 5 modules exists in the database. Each module has ≥ 1 lesson and the course has ≥ 1 quiz question. |
| BRD-FR-042 | The system shall ship with a seeded **GitHub Advanced Security** course containing 5 modules: (1) Overview of GitHub Advanced Security, (2) Code Scanning Basics, (3) Secret Scanning, (4) Dependency Review and Dependabot, (5) Security Workflows and Remediation. | Must Have  | On first launch, a published GitHub Advanced Security course with 5 modules exists in the database. Each module has ≥ 1 lesson and the course has ≥ 1 quiz question. |
| BRD-FR-043 | The system shall ship with a seeded **GitHub Actions** course containing 5 modules: (1) Introduction to Workflows, (2) Workflow Syntax and Triggers, (3) Jobs, Steps, and Runners, (4) Reusable Workflows and Actions, (5) CI/CD Use Cases and Troubleshooting. | Must Have  | On first launch, a published GitHub Actions course with 5 modules exists in the database. Each module has ≥ 1 lesson and the course has ≥ 1 quiz question.       |
| BRD-FR-044 | Each seeded course shall include a course summary, 3–5 modules, 1–3 lessons per module, and at least one quiz per course.                                                                  | Must Have  | Database seed script produces courses meeting all four constraints. Automated test validates structure post-seed.                                |

---

## 7. Non-Functional Requirements

| Req ID      | Category      | Description                                                                                                                                      | Target                                                                                 |
|-------------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| BRD-NFR-001 | Performance   | Non-AI API endpoints (catalog, progress, enrollment, reporting) shall respond within 2 seconds under typical MVP load.                           | P95 response time < 2 s for all non-AI endpoints, measured via integration test timings |
| BRD-NFR-002 | Performance   | AI course generation may run asynchronously; the admin UI shall display a generation-in-progress status and poll for completion.                 | Generation status endpoint returns within 500 ms; full generation completes < 60 s     |
| BRD-NFR-003 | Scalability   | The platform shall support the MVP usage profile: up to 50 concurrent learners and 5 admins without degraded performance.                        | SQLite + FastAPI handles 50 concurrent read requests without 5xx errors                |
| BRD-NFR-004 | Security      | Role-based access control shall be enforced on every API endpoint; no endpoint is accessible without authentication.                            | All protected routes return 401 without a valid session token and 403 for wrong role   |
| BRD-NFR-005 | Security      | API keys and secrets (e.g., `GITHUB_MODELS_API_KEY`) shall never be hardcoded, logged, or returned in API responses.                            | Static analysis scan and code review confirm no secrets in source; test mocks confirm no key leakage in logs |
| BRD-NFR-006 | Security      | All rendered Markdown content (including AI-generated lessons) shall be sanitised to prevent XSS before being served to the browser.             | Automated test: Markdown with `<script>alert(1)</script>` is stripped; no script executes |
| BRD-NFR-007 | Security      | CORS policy shall be appropriately scoped for the deployment environment (no wildcard `*` in production).                                        | CORS headers in production allow only the configured frontend origin                   |
| BRD-NFR-008 | Usability     | A Learner shall be able to reach their next lesson within 2 clicks from the dashboard.                                                           | Manual UX test: dashboard → course → lesson requires ≤ 2 clicks                       |
| BRD-NFR-009 | Usability     | The UI shall be responsive and usable on desktop (≥ 1280 px) and tablet (768–1279 px) screen widths.                                            | Manual cross-device test confirms no layout breakage at 768 px and 1280 px             |
| BRD-NFR-010 | Reliability   | Learner progress shall not be lost on page refresh or accidental navigation away from a lesson.                                                  | ProgressRecord `lastViewedAt` is persisted on lesson open; refresh test confirms data integrity |
| BRD-NFR-011 | Reliability   | AI generation failures (timeout, rate limit, 5xx from GitHub Models) shall not affect Learner access to published courses.                       | Test: with AI service mocked as unavailable, catalog and lesson endpoints return 200 normally |
| BRD-NFR-012 | Reliability   | AI generation failures shall return a clear, retryable error state with an actionable error message rather than a silent failure.                | ContentGenerationRequest status = `failed`; admin UI displays error message and retry button |
| BRD-NFR-013 | Observability | The system shall log authentication events (sign-in, sign-out, failed attempts), course publishing/unpublishing actions, and AI generation calls. | Log entries for all three event types are present after performing each action in a test run |
| BRD-NFR-014 | Observability | The system shall capture AI generation latency and error details in structured log entries.                                                       | Each ContentGenerationRequest log entry contains: requestId, model, latencyMs, status, error (if any) |
| BRD-NFR-015 | Observability | Admin reporting actions shall be traceable to the requesting admin user in the application logs.                                                  | Log entries for reporting endpoints include the authenticated admin's userId              |

---

## 8. Integration Requirements — GitHub Models API

This section captures all requirements for the platform's integration with the GitHub Models API (GPT-4o) for AI-driven course authoring assistance.

| Req ID      | Description                                                                                                                                         | Priority   | Notes                                                                                                    |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------|------------|----------------------------------------------------------------------------------------------------------|
| BRD-INT-001 | The system shall authenticate to the GitHub Models API using the `GITHUB_MODELS_API_KEY` environment variable. The key must never be hardcoded or logged. | Must Have  | Auth method: Bearer token in `Authorization` header. Loaded via `pydantic-settings` at startup.          |
| BRD-INT-002 | The AI generation service shall call the GitHub Models API endpoint configured via the `GITHUB_MODELS_ENDPOINT` environment variable, using GPT-4o as the preferred model. | Must Have  | Model name: `gpt-4o`. Endpoint is configurable to allow easy swap in future without code changes.        |
| BRD-INT-003 | The system shall handle GitHub Models API rate limit responses (HTTP 429) with exponential backoff and a configurable maximum retry count (default: 3). | Must Have  | Retry strategy: exponential backoff starting at 1 s, doubling each retry. After max retries, set ContentGenerationRequest to `failed`. |
| BRD-INT-004 | The system shall wrap all GitHub Models API calls in try/except blocks and return structured error responses; raw API error details must not be exposed to non-admin users. | Must Have  | On non-2xx API response, log full error internally; return sanitised message to admin UI and set request status to `failed`. |
| BRD-INT-005 | The system shall enforce a request timeout of ≤ 60 seconds on all GitHub Models API calls; timed-out requests shall be treated as failures and the retry strategy applied. | Must Have  | Configure `httpx` client timeout at 60 s. On timeout, ContentGenerationRequest status = `failed`.       |
| BRD-INT-006 | The system shall generate structured content conforming to the defined content schema: Course (title, description, audience, objectives[], modules[]), Module (title, summary, lessons[], quiz[]), Lesson (title, markdownContent, estimatedMinutes), QuizQuestion (question, options[], correctAnswer, explanation). | Must Have  | Prompt templates must instruct the model to return JSON conforming to this schema. Pydantic models validate the response before persistence. |
| BRD-INT-007 | The system shall store five reusable prompt templates in the application: (1) Generate course outline, (2) Generate lesson content, (3) Generate quiz questions, (4) Summarise module, (5) Rewrite content for a different skill level. | Must Have  | Templates are stored as application-level configuration or database records. Each generation request references the template used. |
| BRD-INT-008 | The AI generation module shall be designed as a pluggable, modular service with separated layers: prompt orchestration, model invocation, content persistence, and admin review workflow. This design enables future MCP tool exposure without refactoring. | Must Have  | Architecture review confirms the four layers are in distinct functions/classes with no cross-layer coupling. MCP server can be added by wrapping the model invocation layer. |
| BRD-INT-009 | The system shall support exposing or consuming MCP-compatible tools for: generate course outline, generate lesson content, generate quiz questions, fetch course template/context, and validate generated content structure — when MCP is added in a future release. | Nice to Have | No MCP server is required in MVP. The design requirement (BRD-INT-008) ensures readiness. Document the intended tool interface in the design artifacts. |
| BRD-INT-010 | The system shall store generation audit metadata for every GitHub Models API call: promptText, modelUsed, requesterId, generationStatus, createdAt, completedAt, latencyMs, and any error message. | Must Have  | ContentGenerationRequest and ContentGenerationArtifact records are persisted in the database for every generation call, regardless of success or failure. |

### Integration Considerations

- **Model Selection**: GPT-4o is the required model for MVP. It is selected for its strong instruction-following capability with structured JSON output prompts. The `GITHUB_MODELS_ENDPOINT` environment variable keeps the endpoint configurable so an alternative model or provider can be swapped in without code changes.
- **Rate Limits & Quotas**: The GitHub Models API enforces rate limits. The application must handle HTTP 429 with exponential backoff (BRD-INT-003). For MVP scale (a small admin team triggering generation infrequently), rate limits are not expected to be a sustained problem, but the retry logic must be in place from day one.
- **Prompt Management**: Five prompt templates are stored as application-level configuration (BRD-INT-007). Each template is versioned with the generation request metadata so that future prompt changes do not retroactively alter the audit history for existing artifacts.
- **Fallback Strategy**: If the GitHub Models API is unavailable, the admin UI displays a clear error with a retry option (BRD-FR-035). All published course content is served from the local SQLite database and is completely unaffected by AI service unavailability (BRD-NFR-011). There is no automatic fallback to an alternative model in MVP; that is a future enhancement.
- **Content Sanitisation**: All AI-generated Markdown content is sanitised server-side before being stored and again before rendering, to guard against prompt-injected scripts (BRD-FR-037, BRD-NFR-006).

---

## 9. Data Entities

The following entities form the core domain model for the MVP. All entities are persisted in SQLite and defined as Pydantic v2 models.

| Entity                    | Key Attributes                                                                                                                    | Relationships                                              |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| **User**                  | id, name, email (unique), passwordHash, role (`learner`\|`admin`), createdAt                                                      | Has many Enrollments, ProgressRecords, QuizAttempts        |
| **Course**                | id, title, description, status (`draft`\|`published`), difficulty (`beginner`\|`intermediate`\|`advanced`), estimatedDuration, targetAudience, learningObjectives[], tags[], isAiGenerated, createdAt, publishedAt | Has many Modules, Enrollments                              |
| **Module**                | id, courseId (FK), title, summary, sortOrder, quizPassingScore (0–100), isQuizInformational (bool), isAiGenerated, createdAt      | Belongs to Course; has many Lessons, QuizQuestions         |
| **Lesson**                | id, moduleId (FK), title, markdownContent, estimatedMinutes, sortOrder, isAiGenerated, createdAt                                  | Belongs to Module; has many ProgressRecords                |
| **QuizQuestion**          | id, moduleId (FK), question, options[] (2–5 strings), correctAnswer, explanation, sortOrder, isAiGenerated, createdAt             | Belongs to Module; has many QuizAttempts                   |
| **Enrollment**            | id, userId (FK), courseId (FK), enrolledAt, status (`not_started`\|`in_progress`\|`completed`), completedAt, lastLessonId         | Belongs to User and Course                                 |
| **ProgressRecord**        | id, userId (FK), lessonId (FK), moduleId (FK), completed (bool), completedAt, lastViewedAt                                        | Belongs to User, Lesson, Module                            |
| **QuizAttempt**           | id, userId (FK), quizQuestionId (FK), selectedAnswer, isCorrect, attemptedAt                                                      | Belongs to User and QuizQuestion                           |
| **ContentGenerationRequest** | id, promptText, modelUsed, requesterId (FK→User), status (`pending`\|`in_progress`\|`completed`\|`failed`), createdAt, completedAt, latencyMs, errorMessage | Has many ContentGenerationArtifacts                        |
| **ContentGenerationArtifact** | id, sourceRequestId (FK), generatedContent (JSON), contentType (`course`\|`module`\|`lesson`\|`quiz`), approvedBy (FK→User nullable), approvedAt | Belongs to ContentGenerationRequest                        |

---

## 10. API / Service Boundaries

The backend is organised into five service modules under `src/`, exposed via REST endpoints at `/api/v1/`. Frontend pages are served as Jinja2 templates at root paths.

| Service Module          | Responsibility                                                          | Key Endpoints (illustrative)                                                                               |
|-------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| **Auth**                | Sign-in, session management, RBAC enforcement                           | `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`                                                     |
| **Course Management**   | CRUD for courses/modules/lessons/quizQuestions; publish/unpublish; catalog | `GET /api/v1/courses`, `POST /api/v1/courses`, `PATCH /api/v1/courses/{id}/publish`, `GET /api/v1/courses/{id}/modules` |
| **AI Generation**       | GitHub Models integration, prompt templates, draft content persistence   | `POST /api/v1/ai/generate-course`, `POST /api/v1/ai/regenerate-section`, `GET /api/v1/ai/requests/{id}`   |
| **Progress Tracking**   | Enrollment CRUD, lesson/module/course progress, quiz submission/scoring  | `POST /api/v1/enrollments`, `POST /api/v1/progress`, `POST /api/v1/quiz-attempts`, `GET /api/v1/enrollments/{id}/resume` |
| **Reporting**           | Admin dashboard aggregates, enrollment/completion stats, CSV export      | `GET /api/v1/reports/dashboard`, `GET /api/v1/reports/export`                                             |

---

## 11. Risks & Mitigations

| Risk ID | Description                                                                                                                                    | Likelihood | Impact | Mitigation Strategy                                                                                                                                                        |
|---------|------------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| R-001   | **GitHub Models API unavailability or quota exhaustion** — the API is temporarily down or rate-limited, blocking course generation.            | Medium     | High   | Implement exponential backoff with retry (BRD-INT-003). Decouple AI generation from course consumption (BRD-NFR-011). Provide clear admin error messaging with a retry button. |
| R-002   | **Poor AI content quality** — GitHub Models generates inaccurate, irrelevant, or off-brand course content.                                     | Medium     | High   | Mandatory admin review-and-edit step before any AI content is published (BRD-FR-031, BRD-FR-033). Admins can regenerate individual sections (BRD-FR-034). Prompt templates are curated and tested. |
| R-003   | **XSS via AI-generated Markdown** — the model produces content containing malicious scripts or unsafe HTML.                                    | Low        | High   | Server-side Markdown sanitisation before storage and before rendering (BRD-FR-037, BRD-NFR-006). Automated tests with known malicious payloads.                              |
| R-004   | **Learner progress data loss** — database write failure or page navigation causes ProgressRecord to not be persisted.                          | Low        | High   | ProgressRecord written on lesson open (not only on explicit save action) to minimise data loss window (BRD-NFR-010, BRD-FR-021).                                            |
| R-005   | **Scope creep beyond MVP** — stakeholders request features (certificates, SSO, learning paths) that expand scope beyond what is achievable.     | Medium     | Medium | Clear out-of-scope list in Section 4.2. Release slice in Section 12 used to prioritise delivery. Defer non-must-have items to Release 2 or 3.                               |
| R-006   | **SQLite concurrency limits** — SQLite does not support high-concurrency write workloads; at scale, write contention may cause failures.        | Low        | Medium | MVP is scoped to ≤ 50 concurrent learners (BRD-NFR-003). Document migration path to PostgreSQL as a future enhancement. Monitor write latency in observability logs.         |
| R-007   | **API key exposure** — `GITHUB_MODELS_API_KEY` accidentally logged, committed to source control, or returned in an API response.               | Low        | High   | Key loaded only via environment variable / `pydantic-settings` (BRD-INT-001, BRD-NFR-005). Static analysis in CI checks for committed secrets. Never log the key.           |
| R-008   | **Inconsistent prompt schema** — GitHub Models returns content in a structure that does not match the expected Pydantic schema, causing parse errors. | Medium     | Medium | Prompt templates explicitly instruct the model to return strict JSON. Pydantic model validates every response before persistence. Validation failures are caught and returned as a `failed` generation request with the raw response logged for debugging. |
| R-009   | **Adoption failure** — the MVP does not attract sufficient learner usage to validate the concept.                                               | Medium     | Medium | Ship three high-value starter courses immediately (GitHub Foundations, GHAS, GitHub Actions) to provide immediate value. Track KPI-001 through KPI-005 to make an evidence-based go/no-go decision for Release 2. |

---

## 12. Release Slice

### Release 1 — Must Have (MVP)

All `Must Have` requirements from Section 6 and Section 8, plus the seeded starter courses. Core capabilities:

- Sign-in and role-based access control
- Course catalog with search/filter
- Three seeded GitHub courses (Foundations, GHAS, Actions)
- Course structure (Course → Module → Lesson → Quiz)
- Lesson viewer with Markdown rendering
- Quiz support with score recording
- Learner progress tracking with resume
- Admin course CRUD and publish/unpublish
- AI-assisted draft generation using GitHub Models (GPT-4o)
- Draft review, edit, and publish workflow with AI-generated labels
- Admin enrollment management
- Admin reporting dashboard (total learners, enrollments, completion rates, quiz summaries)

### Release 2 — Should Have

All `Should Have` requirements plus prioritised improvements:

- CSV export of progress data (BRD-FR-028)
- Self-enrollment for learners (BRD-FR-015)
- Section-level regeneration (BRD-FR-034)
- Draft vs. published course versioning (BRD-FR-038)
- AI generation audit log for admins (UC-019)
- Module sort order management (BRD-FR-013)
- Better analytics (module-level drop-off rates, AI generation usage by admin)
- Email notifications and reminders to learners

### Release 3 — Nice to Have / Future

- Certificates (lightweight PDF generation)
- Learning paths chaining multiple courses
- Personalised course recommendations
- Multi-tenant / multi-organisation support
- Full MCP tool ecosystem integration (MCP server wrapping the AI generation module)
- SSO / OAuth with corporate identity provider
- Course drop-off analytics by module

---

## 13. Acceptance Criteria Summary

The following acceptance criteria define the minimum bar for MVP completion:

| AC ID  | Acceptance Criterion                                                                                                     | Linked Requirements                     |
|--------|--------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| AC-001 | Admin can create a course manually with all required metadata and publish it to the learner catalog.                     | BRD-FR-009, BRD-FR-010, BRD-FR-007     |
| AC-002 | Admin can generate a full course draft from GitHub Models by providing topic, audience, objectives, difficulty, and desired module count. | BRD-FR-029, BRD-FR-030                  |
| AC-003 | Admin can review, edit individual sections of, and publish the AI-generated course; published content is visible to learners. | BRD-FR-031, BRD-FR-033, BRD-FR-007     |
| AC-004 | Learner can enroll in a published course (admin-assigned or self-enrolled) and see it on their dashboard.                | BRD-FR-014, BRD-FR-015                  |
| AC-005 | Learner can complete all lessons and quiz questions in a course; system marks the enrollment as `completed`.             | BRD-FR-017, BRD-FR-020, BRD-FR-023     |
| AC-006 | System correctly calculates and displays completion percentage (0–100) that updates as the learner progresses.           | BRD-FR-019                              |
| AC-007 | Admin can view per-user and per-course progress (enrollment count, completion %, quiz scores) on the reporting dashboard. | BRD-FR-026, BRD-FR-027                  |
| AC-008 | System includes three seeded starter courses: GitHub Foundations, GitHub Advanced Security, and GitHub Actions — each published and accessible to learners on first launch. | BRD-FR-041, BRD-FR-042, BRD-FR-043     |
| AC-009 | AI generation failures (timeout, 429, 5xx) do not affect learner access to already-published courses; admin receives a retryable error. | BRD-FR-035, BRD-NFR-011                 |
| AC-010 | Rendering Markdown content containing `<script>` tags does not execute JavaScript in the browser.                       | BRD-FR-037, BRD-NFR-006                 |
| AC-011 | A Learner's progress is preserved after a page refresh mid-lesson.                                                       | BRD-FR-021, BRD-NFR-010                 |
| AC-012 | Learner cannot access admin endpoints; Admin cannot view another user's private data through unauthenticated routes.     | BRD-FR-003, BRD-FR-004                  |

---

## 14. Appendix

### 14.1 Glossary

| Term                          | Definition                                                                                                                                                         |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **GitHub Models API**         | A GitHub-hosted REST API that provides access to large language models (including GPT-4o) for inference tasks such as text generation, summarisation, and structured JSON output. Used exclusively for AI-assisted course content generation in this platform. |
| **GPT-4o**                    | The preferred large language model within the GitHub Models API for this platform, selected for its instruction-following capability and structured JSON output support. |
| **GitHub Foundations**        | A beginner-level GitHub training course covering core Git and GitHub concepts: repositories, branches, pull requests, issues, and collaboration workflows.           |
| **GitHub Advanced Security (GHAS)** | A GitHub product providing code scanning, secret scanning, and dependency review features. The GHAS starter course covers these capabilities and remediation workflows. |
| **GitHub Actions**            | GitHub's CI/CD platform for automating workflows. The Actions starter course covers workflow syntax, triggers, jobs, runners, reusable workflows, and CI/CD patterns. |
| **FastAPI**                   | A modern, high-performance Python web framework for building APIs, based on Python type hints and Pydantic for data validation. Used as the backend framework for this platform. |
| **Pydantic v2**               | A Python data validation library used for defining request/response schemas and loading application configuration from environment variables (`pydantic-settings`).  |
| **SQLite**                    | A lightweight, file-based relational database. Used as the MVP database for zero-configuration local storage. Migration to PostgreSQL is a future enhancement.       |
| **Jinja2**                    | A Python templating engine used to server-render HTML pages for the frontend.                                                                                       |
| **MCP (Model Context Protocol)** | An emerging standard protocol for connecting applications to model-aware tools and contextual data sources. The AI generation service is designed to be MCP-compatible for future integration. |
| **Draft**                     | The status of a course or AI-generated content artifact that has not yet been reviewed and published by an admin. Draft content is not visible to learners.          |
| **Published**                 | The status of a course that has been explicitly approved and published by an admin. Published courses are visible in the learner catalog.                            |
| **ContentGenerationRequest**  | A database record capturing the inputs, metadata, and status of a single GitHub Models API generation call.                                                        |
| **ContentGenerationArtifact** | A database record containing the structured JSON content output by a ContentGenerationRequest, along with approval metadata.                                        |
| **ProgressRecord**            | A database record linking a User to a Lesson, tracking whether the lesson has been completed and when it was last viewed.                                           |
| **RBAC**                      | Role-Based Access Control — the security model used to restrict actions to users with the appropriate role (`learner` or `admin`).                                  |
| **XSS (Cross-Site Scripting)**| A web security vulnerability where malicious scripts are injected into content rendered in a browser. The platform sanitises all Markdown content to prevent this.  |
| **Enrollment**                | A record linking a User to a Course, tracking their enrollment status (not_started / in_progress / completed) and progress.                                         |

### 14.2 References

| Reference                           | Description / Link                                                                                              |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Product Requirements Document       | `learning-platform-mvp-requirements.md` — authoritative source for all scope, user journeys, and acceptance criteria (repository root) |
| Copilot Instructions                | `.github/copilot-instructions.md` — tech stack, domain model, coding conventions, and agent workflow rules     |
| BRD Template                        | `templates/BRD.md` — structural template from which this document was produced                                 |
| GitHub Models API Documentation     | https://docs.github.com/en/github-models                                                                       |
| FastAPI Documentation               | https://fastapi.tiangolo.com/                                                                                   |
| Pydantic v2 Documentation           | https://docs.pydantic.dev/latest/                                                                              |
| SQLite Documentation                | https://www.sqlite.org/docs.html                                                                               |
| Model Context Protocol (MCP)        | https://modelcontextprotocol.io/ — future integration target for AI generation tool exposure                   |
