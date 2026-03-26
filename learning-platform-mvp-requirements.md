# Learning Platform MVP Requirements

## 1. Purpose

Build a minimum viable learning platform where:
- **Learners** can enroll in and complete courses.
- **Admins** can create and manage courses, assign learners, and track progress.
- **Course content** can be created dynamically with **GitHub Models** assistance.
- The MVP ships with a small starter catalog:
  - GitHub Foundations
  - GitHub Advanced Security
  - GitHub Actions

The goal of the MVP is to validate that teams can onboard users into GitHub learning journeys, measure progress, and reduce manual content authoring effort through AI-assisted course generation.

---

## 2. MVP Goals

### Business goals
- Provide a simple internal/external training experience focused on GitHub topics.
- Enable admins to measure learner progress and completion.
- Reduce content authoring time by using GitHub Models to generate course drafts.
- Validate interest before investing in a full-featured LMS.

### User goals
- Learners can quickly find assigned courses and continue where they left off.
- Learners can complete short lessons and quizzes.
- Admins can easily view enrollment and completion status.
- Admins can generate or update course content with minimal effort.

### Success criteria
- Admin can publish at least 3 courses.
- Learner can enroll in and complete a course end-to-end.
- Admin can view per-user and per-course progress.
- GitHub Models can generate draft course modules, quiz questions, and summaries that admins can review before publishing.

---

## 3. Users and Roles

### 3.1 Learner
A user who consumes courses and completes learning activities.

**Needs:**
- Sign in securely.
- View assigned or available courses.
- Track personal progress.
- Resume from last lesson.
- Take quizzes and see completion status.

### 3.2 Admin
A user who manages catalog, enrollments, and reporting.

**Needs:**
- Create/edit/publish courses.
- Use GitHub Models to draft course content.
- Enroll learners.
- Track course completion and learner progress.
- Review and approve AI-generated course content before publishing.

### 3.3 Optional future role (not required for MVP)
- **Content Author**: separate from admin, for authoring only.

---

## 4. Scope

### In scope for MVP
- Authentication and role-based access (Learner, Admin).
- Course catalog with a few GitHub-focused courses.
- Course structure: course → modules → lessons → quiz.
- Lesson types: text, links, embedded media, markdown.
- Learner progress tracking at module/course level.
- Admin dashboard for tracking enrollments and completion.
- AI-assisted course generation using GitHub Models.
- Manual review and publishing flow for AI-generated content.
- Basic search/filter for course catalog.
- Starter seed content for:
  - GitHub Foundations
  - GitHub Advanced Security
  - GitHub Actions

### Out of scope for MVP
- Payments or subscriptions.
- Certificates with advanced verification.
- Social features (comments, likes, forums).
- Native mobile apps.
- SCORM/xAPI compliance.
- Advanced adaptive learning.
- Multiple organizations/tenants unless required later.
- Deep integrations with enterprise HR/LMS tools.

---

## 5. Core User Journeys

### 5.1 Learner journey
1. Learner signs in.
2. Learner sees assigned or available courses.
3. Learner opens a course and views modules/lessons.
4. Learner completes lessons and quiz questions.
5. System saves progress automatically.
6. Learner sees percent complete and completion status.

### 5.2 Admin course management journey
1. Admin signs in.
2. Admin creates a new course or selects an existing draft.
3. Admin enters topic, audience, learning objectives, difficulty, and desired duration.
4. Admin uses GitHub Models to generate:
   - course outline
   - lesson drafts
   - quiz questions
   - summaries or key takeaways
5. Admin reviews and edits generated content.
6. Admin publishes the course.
7. Admin assigns learners or makes the course available in catalog.

### 5.3 Admin reporting journey
1. Admin opens dashboard.
2. Admin filters by course, learner, or status.
3. Admin views enrollments, completion percentages, module-level progress, and quiz performance.
4. Admin exports basic progress data if needed.

---

## 6. Functional Requirements

## 6.1 Authentication and authorization
- The system shall allow users to sign in securely.
- The system shall support at least two roles: `Learner` and `Admin`.
- The system shall restrict course authoring, publishing, and reporting to admins.
- The system shall allow learners to access only their own learning progress.

## 6.2 Course catalog
- The system shall display a catalog of published courses.
- The system shall show course title, description, difficulty, estimated duration, and status.
- The system shall support filtering by topic and difficulty.
- The system shall allow admins to publish/unpublish courses.

## 6.3 Course structure
- The system shall support:
  - Course metadata
  - Modules
  - Lessons
  - Quiz questions
- Each course shall include:
  - title
  - summary
  - target audience
  - learning objectives
  - estimated duration
  - difficulty level
  - tags
- Each lesson shall support markdown or rich text content.
- Each module may include a quiz or knowledge check.

## 6.4 Enrollment
- The system shall allow admins to assign courses to learners.
- The system may also allow self-enrollment for published courses in MVP if desired.
- The system shall track enrollment status: not started, in progress, completed.

## 6.5 Learner progress tracking
- The system shall persist learner progress per lesson/module/course.
- The system shall record the last accessed lesson.
- The system shall calculate completion percentage.
- The system shall mark a course complete when all required modules/quizzes are completed.
- The system shall display progress to both learner and admin.

## 6.6 Quizzes and assessments
- The system shall support multiple-choice questions for MVP.
- The system shall record learner answers and score.
- The system shall show pass/fail or score summary.
- The system shall allow admins to configure passing score or mark quiz as informational only.

## 6.7 Admin reporting
- The system shall provide a dashboard for admins.
- The dashboard shall show:
  - total learners
  - enrollments per course
  - completion rates
  - in-progress counts
  - quiz score summaries
- The system shall allow filtering by course and learner.
- The system should support CSV export for MVP if low effort.

## 6.8 AI-assisted course generation with GitHub Models
- The system shall allow admins to generate course drafts using GitHub Models.
- The admin shall provide prompts/inputs such as:
  - course topic
  - intended audience
  - learning objectives
  - difficulty
  - desired number of modules
  - preferred tone/style
- The system shall generate:
  - course title suggestions
  - course description
  - module outline
  - lesson draft content
  - quiz questions and answers
  - key takeaways
- The system shall save generated content as **draft**, not auto-publish.
- The system shall require admin review/edit before publishing.
- The system shall keep prompt and generation metadata for audit/debugging.
- The system should support regenerating an individual section rather than the whole course.

## 6.9 Course versioning
- The system should support draft vs published versions.
- The system should preserve previously published course content when editing a draft.
- The system may maintain a simple revision history for admin visibility.

---

## 7. Starter Course Requirements

The MVP should seed the following courses:

### 7.1 GitHub Foundations
Suggested modules:
- Introduction to Git and GitHub
- Repositories, branches, and commits
- Pull requests and code reviews
- Issues and project basics
- Collaboration best practices

### 7.2 GitHub Advanced Security
Suggested modules:
- Overview of GitHub Advanced Security
- Code scanning basics
- Secret scanning
- Dependency review and Dependabot
- Security workflows and remediation

### 7.3 GitHub Actions
Suggested modules:
- Introduction to workflows
- Workflow syntax and triggers
- Jobs, steps, and runners
- Reusable workflows and actions
- CI/CD use cases and troubleshooting

For each starter course, the system should include:
- course summary
- 3–5 modules
- 1–3 lessons per module
- at least one quiz per course

---

## 8. GitHub Models Requirements

## 8.1 Purpose of GitHub Models in MVP
GitHub Models will be used as the AI generation layer for course authoring assistance.

## 8.2 Required capabilities
- Prompt-based generation of structured course content.
- Support for generating content in a predictable schema or JSON structure.
- Ability to produce markdown-ready lesson content.
- Ability to generate quiz questions with correct answer metadata.
- Ability to regenerate sections on request.

## 8.3 Prompting requirements
The application should define reusable prompt templates for:
- Generate course outline
- Generate lesson content
- Generate quiz questions
- Summarize module
- Rewrite content for a different skill level

## 8.4 Safety and quality requirements
- AI-generated content must be reviewable by admins before publication.
- The application should label content as AI-generated draft until approved.
- The application should store the prompt, model used, timestamp, and generation status.
- The application should prevent unsupported markdown/scripts from rendering unsafely.

## 8.5 Data contract for generated content
Recommended content object shape:
- Course
  - title
  - description
  - audience
  - objectives[]
  - modules[]
- Module
  - title
  - summary
  - lessons[]
  - quiz[]
- Lesson
  - title
  - markdownContent
  - estimatedMinutes
- QuizQuestion
  - question
  - options[]
  - correctAnswer
  - explanation

---

## 9. MCP Requirements

Assumption: MCP refers to **Model Context Protocol** support for connecting the app or admin tooling to model-aware tools and prompts.

### 9.1 Why MCP may matter
MCP can help standardize how the platform accesses tools, prompts, or contextual data for AI-assisted course creation and admin workflows.

### 9.2 MVP-level MCP requirements
- The solution should support a pluggable integration layer for AI/model tools.
- The AI generation workflow should be designed so that model requests can later be exposed through MCP-compatible tools or services.
- The system should separate:
  - prompt orchestration
  - model invocation
  - content persistence
  - admin review workflow
- If MCP is implemented in MVP, the application should expose or consume tools for:
  - generate course outline
  - generate lesson content
  - generate quiz questions
  - fetch course template/context
  - validate generated content structure

### 9.3 MCP server considerations
If an MCP server is included, it should support:
- Tool definitions for course generation tasks.
- Input validation for structured generation requests.
- Authentication/authorization for admin-only generation actions.
- Logging and request tracing.
- Rate limit/error handling for model calls.
- Standard response schema for generated course artifacts.

### 9.4 MCP non-functional requirements
- Secure handling of tokens/credentials.
- Clear separation between user-facing app APIs and MCP tool endpoints.
- Audit trail for admin-triggered AI generation.
- Timeout and retry strategy for model calls.
- Ability to swap model providers later with minimal impact.

### 9.5 Recommendation for MVP
MCP support is **nice-to-have** unless the team already plans tool-based orchestration. For MVP, the most important design choice is to keep the AI generation service modular so MCP can be added without refactoring the entire app.

---

## 10. Non-Functional Requirements

## 10.1 Usability
- The learner experience should be simple and low-friction.
- The UI should be responsive for desktop and tablet.
- Learners should reach their next lesson within 2 clicks from dashboard.

## 10.2 Performance
- Course catalog and dashboards should load within acceptable interactive time for typical MVP usage.
- Progress updates should save without noticeable delay.
- AI generation may be asynchronous if generation time is long.

## 10.3 Security
- Role-based access control is required.
- Admin-only operations must be protected.
- User progress data must only be visible to authorized users.
- Secrets/tokens for GitHub Models must be stored securely.
- Rendered lesson content must be sanitized to prevent XSS.

## 10.4 Reliability
- Progress should not be lost if the learner refreshes the page.
- AI generation failures should return clear retryable error states.
- Published courses should remain available even if model services are down.

## 10.5 Observability
- The system should log authentication events, course publishing, and AI generation actions.
- The system should capture generation errors and latency.
- Admin reporting actions should be traceable.

---

## 11. Suggested Data Entities

Minimum entities for MVP:
- User
- Role
- Course
- Module
- Lesson
- QuizQuestion
- Enrollment
- ProgressRecord
- QuizAttempt
- ContentGenerationRequest
- ContentGenerationArtifact

### Example entity expectations
- **User**: id, name, email, role
- **Course**: id, title, description, status, difficulty, estimatedDuration
- **Enrollment**: userId, courseId, enrolledAt, status
- **ProgressRecord**: userId, lessonId/moduleId, completed, completedAt, lastViewedAt
- **ContentGenerationRequest**: prompt, model, requester, status, createdAt

---

## 12. API / Service Requirements

The platform should support services or APIs for:
- authentication
- course catalog retrieval
- course authoring and publishing
- enrollment management
- progress tracking
- quiz submission
- reporting
- AI generation workflow

Recommended backend service boundaries:
- Auth service/module
- Course management service/module
- Progress tracking service/module
- Reporting service/module
- AI generation service/module

---

## 13. Admin Content Governance Requirements

- All AI-generated content must start in draft status.
- Admins must be able to edit generated content before publishing.
- Admins should be able to approve/reject/regenerate generated modules.
- The system should indicate which sections were AI-generated.
- The system should retain enough metadata to troubleshoot low-quality generations.

---

## 14. Analytics Requirements

Minimum analytics for MVP:
- Number of enrollments per course
- Number of completions per course
- Learner progress percentage
- Average quiz score per course
- Course drop-off point by module (nice-to-have)
- AI generation usage count by admin (nice-to-have)

---

## 15. Assumptions and Open Questions

### Assumptions
- The MVP is for a single organization or simple shared environment.
- Only admins create/manage courses.
- AI generation is assistive, not autonomous.
- GitHub Models access is available to the team building/administering the platform.

### Open questions
- Should learners self-enroll or only be admin-assigned?
- Is this internal-only SSO or public sign-up?
- Are certificates required even in lightweight form?
- Do admins need CSV export in MVP or can dashboard-only reporting suffice?
- Is MCP required in the first release or should architecture simply remain MCP-ready?
- Should quiz passing be mandatory for course completion?

---

## 16. Recommended MVP Release Slice

### Release 1 (must-have)
- Sign in
- Role-based access
- Course catalog
- 3 seeded GitHub courses
- Lesson viewer
- Quiz support
- Progress tracking
- Admin dashboard
- AI-assisted draft generation using GitHub Models
- Draft review/edit/publish workflow

### Release 2 (should-have)
- CSV export
- Course version history
- Regenerate specific modules/lessons
- Better analytics
- Notifications/reminders

### Release 3 (future)
- Certificates
- Learning paths
- Recommendations
- Multi-tenant org support
- Full MCP tool ecosystem integration

---

## 17. Recommended Acceptance Criteria for MVP

- Admin can create a course manually.
- Admin can generate a course draft from GitHub Models.
- Admin can review, edit, and publish generated content.
- Learner can enroll in or access a published course.
- Learner can complete lessons and quiz questions.
- System correctly tracks completion percentage.
- Admin can view learner progress by course.
- System includes starter courses for GitHub Foundations, GitHub Advanced Security, and GitHub Actions.
- AI generation failures do not block the rest of the platform.
- Published course consumption works even if AI services are temporarily unavailable.
