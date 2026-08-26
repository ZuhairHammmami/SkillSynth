# SS-EDS: Functional Requirements

## Purpose
Catalog the functional requirements implemented by SkillSynth and map each to its live endpoints and tests. Covers auth, assessment, path generation, progress, analytics, admin management, and realtime.

## Responsibilities
- Maintain requirement-to-implementation traceability
- Define acceptance criteria per feature area
- Map requirements to the 15-table schema and 49 API paths

## Inputs
- Product scope (01-product)
- Domain model (05-domain)
- Endpoint inventory (22-api)

## Outputs
- Requirements traceability (this document)
- Coverage evidence via tests/ (190 tests)

## Dependencies
- 22-api (endpoints implement requirements)
- 07-backend (backend fulfills requirements)
- 08-frontend / 09-admin (UI implements requirements)
- 16-testing (tests verify requirements)

## Sequence: Requirement to Release
```
Req ID → Spec → Implementation → pytest/tsc/lint → Merge
                          ↓ fail
                     Back to implementation
```

## State Diagram: Requirement Status
```
[Drafted] → [Approved] → [Implemented] → [Verified]
                ↓
           [Rejected]
```

## ERD References
- All 15 tables serve functional requirements
- Junction tables: skill_prerequisites (prerequisite DAG), job_role_skills (role→skill weighting)

## Requirement Areas (current)
| ID Area | Requirement | Implementation |
|---------|-------------|----------------|
| FR-AUTH | Register/login with email+password; JWT bearer auth | POST /api/auth/register, POST /api/auth/token; lockout after 5 failures/15 min |
| FR-AUTH-2 | Self-service password change and reset | POST /api/auth/change-password, forgot-password, reset-password (30-min signed token) |
| FR-ASSESS | Fetch question set for a skill or job role | GET /api/assessments/{skill_id}/questions, GET /api/assessments/role/{job_role_title} |
| FR-ASSESS-2 | Score submission updates user_skills proficiency (0–5) | POST /api/assessments/submit |
| FR-PATH | Wizard (job role + preferences) generates a prerequisite-ordered path | POST /api/generate-path/ (= POST /api/learning/generate); Kahn topological sort over skill_prerequisites |
| FR-PATH-2 | Inspect graph and skill gaps | GET /api/learning/graph, GET /api/learning/gaps |
| FR-PROG | Complete/undo steps; view progress dashboard | POST /api/steps/{id}/complete, undo-complete, GET /api/progress/dashboard |
| FR-ANA | Learning dashboard, growth, history | GET /api/analytics/* (4 reads) |
| FR-REAL | Live notification of path generation and assessment completion | SSE at GET /api/realtime/events (+ /api/events alias) |
| FR-ADMIN | Full CRUD over users/skills/categories/resources/job-roles/assessments | /api/admin/* (30 operations, admin-gated) |
| FR-ADMIN-2 | Restricted deletes with dependency census | DELETE skills/categories/job-roles return 409 unless `?force=true` (ADR-014) |
| FR-ADMIN-3 | Backups, DB inspector, feature flags, reports, audit feed | GET/POST /api/admin/backups, db-inspector, feature-flags, reports/*, events |

## Rules
1. Every requirement maps to at least one endpoint in 22-api and one test file in tests/
2. Acceptance criteria are measurable (status codes, payload fields)
3. Requirements specify RTL/i18n behavior for any student-facing surface
4. Integrity violations are rejected deterministically: FK miss → 400; rename conflict on update → 409; cycles → 400; DB IntegrityError → 409

## Examples
- FR-PATH acceptance: generated path's steps respect every skill_prerequisites edge (verified by test_learning.py)
- FR-ADMIN-2 acceptance: deleting a category with children returns 409 + census list (test_catalog_integrity.py)

## Edge Cases
- Concurrent generation for the same user → each request creates an independent path
- Reset token reuse after consumption → 400 (stateless single-use semantics)

## Failure Cases
- Implementation diverges from requirement → failed review
- Missing test coverage for a new endpoint → blocked merge

## Recovery Procedures
1. Update the spec or the implementation until they match
2. Add the missing test, re-run `PYTHONPATH=src python -m pytest tests/ -q`

## Refactoring Strategy
- Requirements versioned alongside code in this section
- Deprecated requirements archived with an ADR reference
