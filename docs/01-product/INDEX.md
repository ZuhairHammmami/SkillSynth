# SS-EDS: Product

## Purpose
Define SkillSynth as a bilingual adaptive-learning platform: assessment-driven skill profiling, prerequisite-aware learning-path generation, progress tracking, and analytics — with a separate admin application for content and user management.

## Responsibilities
- Maintain the product feature catalog (current, shipped features only)
- Define personas: learner (student frontend), admin (admin app)
- Track verification status via tests/ and build gates

## Inputs
- Stakeholder requirements
- Domain model (05-domain)
- User feedback on the learning workflow

## Outputs
- Feature registry (this document)
- Release notes (docs/45-release-notes/)
- Decision records for scope changes (docs/41-decision-records/)

## Dependencies
- 02-business (operational model)
- 03-functional-requirements (feature-level requirements)
- 00-principles (design philosophy constrains product)

## Sequence: Feature Lifecycle
```
Idea → Spec → Review → Implementation → Tests (142 pytest + tsc/lint/build) → Merge
```

## State Diagram: Feature Status
```
[Proposed] → [In Development] → [Tested] → [Shipped]
                  ↓                     ↓
             [Rejected]           [Removed] (documented in ADRs)
```

## ERD References
- docs/10-database/ — 15-table schema backing all features
- docs/40-diagrams/ERD.md

## Current Feature Set
| Area | Features |
|------|----------|
| Auth | Register/login (JWT), change password, forgot/reset password, account lockout |
| Assessment | Per-skill question sets, role-based assessments, scoring → user_skills proficiency |
| Path generation | Wizard (job role + preferences) → scored skill plan → topologically sorted path |
| Progress | Step complete/undo, progress dashboard, per-path detail |
| Analytics | Dashboard, skill growth, path progress, learning history |
| Realtime | SSE stream (path_generated, assessment_completed) |
| Admin | Users/skills/categories/resources/job-roles/assessments CRUD, paths view, reports, backups, audit logs |

Historical context (one line): role-permission tables, gamification, notifications, and vector search existed in earlier phases and were removed outright (docs/41-decision-records/, esp. ADR-013).

## Rules
1. No feature ships without ar/en i18n coverage in the student frontend
2. Every feature must work RTL-first
3. Every content type must have an admin management path
4. Every backend change lands with passing tests before merge

## Examples
- Learner completes the wizard → POST /api/generate-path/ → persisted path with ordered steps
- Admin edits a skill → PUT /api/admin/skills/{id} → case-insensitive rename uniqueness enforced

## Edge Cases
- New user with empty skill profile → no skills skipped during generation
- Dependent rows exist on admin delete → 409 census unless `?force=true` (ADR-014)

## Failure Cases
- Feature breaks `pnpm type-check` or the pytest suite → blocked from merge
- Missing i18n key → key name renders; caught by review

## Recovery Procedures
1. Revert the offending commit
2. File a fix PR with required i18n/tests
3. Document any permanent removal in an ADR

## Refactoring Strategy
- Removed features are deleted outright with their tables/endpoints (no dead flags)
- Quarterly review of the feature catalog against actual routes (22-api)
