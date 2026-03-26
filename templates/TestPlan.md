# Test Plan — AI-Powered Learning Platform

| Field         | Value                              |
|---------------|------------------------------------|
| **Version**   | [Fill in, e.g. 1.0]               |
| **Date**      | [Fill in]                          |
| **Author**    | [Fill in]                          |
| **BRD Ref**   | [Fill in, e.g. BRD-LP-001]        |
| **Status**    | Draft                              |

---

## 1. Test Scope & Objectives

### 1.1 Scope

This test plan covers the MVP of the AI-powered learning platform built with Python, FastAPI, and the GitHub Models API. The MVP delivers personalised training content for three topics:

- GitHub Actions
- GitHub Copilot
- GitHub Advanced Security

**In scope:**
- FastAPI REST endpoints (topic listing, content generation, progress tracking)
- Integration with GitHub Models API for content generation
- Input validation and error handling
- Authentication and authorisation flows
- Core business logic and data models

**Out of scope:**
- [Fill in — e.g. UI/frontend, load/performance testing for MVP]

### 1.2 Objectives

- Verify all API endpoints return correct responses for valid and invalid inputs
- Confirm GitHub Models API integration produces expected learning content
- Validate business rules for the three MVP training topics
- Ensure error handling returns appropriate HTTP status codes and messages
- Achieve minimum code coverage target of [Fill in, e.g. 80%]

---

## 2. Test Strategy

### 2.1 Unit Testing

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| **Scope**       | Individual functions, models, utility helpers                 |
| **Framework**   | pytest                                                        |
| **Approach**    | Mock external dependencies (GitHub Models API, DB); test business logic in isolation |
| **Coverage**    | Target [Fill in]% line coverage                               |

### 2.2 Integration Testing

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| **Scope**       | Interaction between modules — routes → services → models      |
| **Framework**   | pytest + httpx (async)                                        |
| **Approach**    | Use FastAPI `TestClient`; mock only external APIs             |

### 2.3 API Testing

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| **Scope**       | All REST endpoints — happy path, edge cases, error responses  |
| **Framework**   | pytest + httpx                                                |
| **Approach**    | Validate status codes, response schemas, headers, auth flows  |

### 2.4 End-to-End Testing

| Aspect          | Detail                                                        |
|-----------------|---------------------------------------------------------------|
| **Scope**       | Full request lifecycle: API call → GitHub Models API → response |
| **Framework**   | pytest (with live or recorded fixtures)                       |
| **Approach**    | Limited E2E tests against staging; use VCR/recorded cassettes for CI |

---

## 3. Test Environment

### 3.1 Local Development Setup

| Component               | Detail                                     |
|-------------------------|--------------------------------------------|
| **Python version**      | [Fill in, e.g. 3.11+]                     |
| **Virtual environment** | venv / poetry                              |
| **Application server**  | Uvicorn (FastAPI)                          |
| **Database**            | [Fill in, e.g. SQLite for tests / PostgreSQL] |
| **External APIs**       | GitHub Models API (mocked in unit/integration tests) |

### 3.2 Dependencies

```
pytest
httpx
pytest-asyncio
pytest-cov
respx          # mock httpx calls to GitHub Models API
```

### 3.3 Environment Variables

| Variable                    | Purpose                              |
|-----------------------------|--------------------------------------|
| `GITHUB_MODELS_API_KEY`    | API key for GitHub Models (use test/mock value in CI) |
| `APP_ENV`                  | Set to `test` during test runs       |
| [Fill in additional vars]  | [Fill in]                            |

---

## 4. Test Cases

| TC ID   | Description                                           | Type        | Input                              | Expected Output                                    | BRD/Story Ref | Status      |
|---------|-------------------------------------------------------|-------------|------------------------------------|----------------------------------------------------|----------------|-------------|
| TC-001  | List available training topics                        | API         | `GET /topics`                      | 200 OK; JSON array with 3 topics                   | [Fill in]      | Not Started |
| TC-002  | Get details for a valid topic (GitHub Actions)        | API         | `GET /topics/github-actions`       | 200 OK; topic metadata and description             | [Fill in]      | Not Started |
| TC-003  | Get details for a non-existent topic                  | API         | `GET /topics/invalid-topic`        | 404 Not Found; error message                       | [Fill in]      | Not Started |
| TC-004  | Generate learning content for GitHub Copilot          | Integration | `POST /generate` with valid payload| 200 OK; AI-generated content for Copilot topic     | [Fill in]      | Not Started |
| TC-005  | Generate content with missing required fields         | API         | `POST /generate` missing `topic`   | 422 Unprocessable Entity; validation error details | [Fill in]      | Not Started |
| TC-006  | Handle GitHub Models API timeout gracefully           | Integration | Simulated timeout on external call | 503 Service Unavailable; retry guidance             | [Fill in]      | Not Started |
| TC-007  | Validate topic enum — only MVP topics accepted        | Unit        | Topic value not in allowed list    | Validation error raised                            | [Fill in]      | Not Started |
| TC-008  | Track user progress for a topic                       | API         | `POST /progress` with valid data   | 200 OK; progress saved                             | [Fill in]      | Not Started |
| TC-009  | Retrieve user progress                                | API         | `GET /progress/{user_id}`          | 200 OK; progress summary across topics             | [Fill in]      | Not Started |
| TC-010  | Unauthenticated request to protected endpoint         | API         | Request without auth token         | 401 Unauthorised                                   | [Fill in]      | Not Started |
| TC-0XX  | [Fill in additional test cases]                       | [Fill in]   | [Fill in]                          | [Fill in]                                          | [Fill in]      | Not Started |

---

## 5. Test Data Requirements

| Data Category          | Description                                               | Source           |
|------------------------|-----------------------------------------------------------|------------------|
| Training topics        | Seed data for 3 MVP topics (Actions, Copilot, Adv. Security) | Fixtures / factory |
| User accounts          | Test user with valid credentials                          | Fixtures         |
| API responses          | Recorded GitHub Models API responses for deterministic tests | VCR cassettes    |
| Invalid inputs         | Malformed JSON, missing fields, SQL injection strings     | Parameterised fixtures |
| [Fill in]              | [Fill in]                                                 | [Fill in]        |

---

## 6. Entry / Exit Criteria

### 6.1 Entry Criteria

- [ ] Application builds and starts without errors
- [ ] Test environment provisioned with required dependencies
- [ ] Test data and fixtures are available
- [ ] All external API mocks are configured and verified
- [ ] [Fill in additional criteria]

### 6.2 Exit Criteria

- [ ] All critical and high-priority test cases pass
- [ ] Code coverage ≥ [Fill in]%
- [ ] No open Severity 1 or Severity 2 defects
- [ ] API contract tests pass for all endpoints
- [ ] [Fill in additional criteria]

---

## 7. Defect Management

### 7.1 Severity Levels

| Severity | Definition                                                     | Example                                    |
|----------|----------------------------------------------------------------|--------------------------------------------|
| **S1 — Critical** | System crash, data loss, security vulnerability        | API returns 500 on all requests            |
| **S2 — High**     | Major feature broken, no workaround                   | Content generation fails for a topic       |
| **S3 — Medium**   | Feature impaired but workaround exists                | Progress not saved on first attempt        |
| **S4 — Low**      | Minor issue, cosmetic, or edge case                   | Inconsistent error message wording         |

### 7.2 Defect Workflow

```
New → Triaged → In Progress → Fixed → Verified → Closed
                                   ↘ Won't Fix
```

- Defects tracked in: [Fill in — e.g. GitHub Issues with `bug` label]
- Retest owner: [Fill in]

---

## 8. Tools & Frameworks

| Tool / Framework | Purpose                                          |
|------------------|--------------------------------------------------|
| **pytest**       | Test runner and assertion framework              |
| **httpx**        | Async HTTP client for API testing                |
| **pytest-asyncio** | Async test support for FastAPI                 |
| **pytest-cov**   | Code coverage reporting                          |
| **respx**        | Mock httpx requests (GitHub Models API stubs)    |
| **Ruff / mypy**  | Linting and type checking (pre-test gates)       |
| **GitHub Actions** | CI pipeline — run tests on push/PR             |

---

## 9. Traceability Matrix

| BRD Requirement          | Story/Task   | Test Cases              | Status      |
|--------------------------|--------------|-------------------------|-------------|
| [Fill in — e.g. REQ-01: Topic listing]    | [Fill in]    | TC-001, TC-002, TC-003  | Not Started |
| [Fill in — e.g. REQ-02: Content generation] | [Fill in]  | TC-004, TC-005, TC-006  | Not Started |
| [Fill in — e.g. REQ-03: Progress tracking]  | [Fill in]  | TC-008, TC-009          | Not Started |
| [Fill in — e.g. REQ-04: Authentication]     | [Fill in]  | TC-010                  | Not Started |
| [Fill in]                | [Fill in]    | [Fill in]               | Not Started |

---

## 10. Risks & Assumptions

### 10.1 Risks

| Risk                                              | Impact | Likelihood | Mitigation                                       |
|---------------------------------------------------|--------|------------|--------------------------------------------------|
| GitHub Models API rate limits during testing       | High   | Medium     | Use mocked/recorded responses in CI; live tests only in staging |
| Non-deterministic AI responses complicate assertions | Medium | High     | Assert on structure/schema rather than exact content |
| Test environment drift from production config      | Medium | Low        | Infrastructure-as-code; containerised test env   |
| [Fill in]                                         | [Fill in] | [Fill in] | [Fill in]                                       |

### 10.2 Assumptions

- GitHub Models API remains available and backward-compatible during MVP development
- Three MVP topics (Actions, Copilot, Advanced Security) are finalised and will not change scope
- pytest and httpx are the agreed-upon testing stack
- [Fill in additional assumptions]

---

*Template maintained for use by the `automation-test-agent`. Generated test artifacts should follow this structure and reference the corresponding BRD and Story IDs.*
