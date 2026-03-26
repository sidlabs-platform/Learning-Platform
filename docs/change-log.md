# Change Log

This file records significant decisions, artifact creations, and notable changes made during the SDLC lifecycle of the Learning Platform MVP.

---

## Entries

| Date       | Author               | Type            | Summary                                                                                                                                                                                                               |
|------------|----------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-03-26 | 1-requirement-agent  | BRD Created     | Produced the initial Business Requirements Document (`docs/requirements/BRD.md` v1.0). Document covers: executive summary, 5 KPIs, background and context, stakeholders, full in-scope/out-of-scope definition, 20 use cases spanning learner journey / admin course management / admin reporting, 44 functional requirements (BRD-FR-001–BRD-FR-044) with acceptance criteria and priority levels, 15 non-functional requirements (BRD-NFR-001–BRD-NFR-015), 10 GitHub Models integration requirements (BRD-INT-001–BRD-INT-010) with full data contract and fallback strategy, complete data entity definitions for all 10 domain entities, API/service boundary table, 9 identified risks with mitigations, a 3-release delivery slice, 12 acceptance criteria linked to requirement IDs, and a glossary of 17 terms. Source: `learning-platform-mvp-requirements.md` and `.github/copilot-instructions.md`. |
| 2026-03-26 | 2-plan-and-design-agent | HLD + LLD Created | Produced the High-Level Design (`docs/design/HLD.md` v1.0) and 7 Low-Level Design documents (`docs/design/LLD/`) covering all system components (COMP-001 through COMP-007). **Key architecture decisions**: (DD-001) SQLite + SQLAlchemy async for zero-config MVP persistence; (DD-002) JWT in HTTP-only SameSite=Strict cookies for XSS-resistant authentication; (DD-003) FastAPI BackgroundTasks for async AI generation (no broker/queue required); (DD-004) Jinja2 SSR + Vanilla JS (tech stack constraint); (DD-005) Server-side bleach sanitisation at write and render (defence-in-depth XSS prevention); (DD-006) 4-layer AI generation module for MCP readiness (Prompt Orchestration → Model Invocation → Content Persistence → Review Workflow); (DD-007) Simple draft/published status flag for MVP course versioning; (DD-008) Prompt templates as code constants (version-controlled and testable). Full BRD traceability: all 44 FRs, 15 NFRs, and 10 INT requirements mapped to at least one component. |

---

*Append a new row to the table above for each significant change, decision, or artifact produced.*
