# SS-EDS: Roadmaps

## Purpose
Document the product and feature roadmaps for SkillSynth, tracking completed phases, current work, and planned future enhancements.

## Responsibilities
- Maintain phase completion tracker (11 phases complete)
- Define future roadmap items
- Track feature maturity and integration status
- Document architectural evolution plans

## Inputs
- Product requirements (01-product)
- Phase completion status
- Stakeholder feedback
- Technical debt assessment

## Outputs
- Phase roadmap (past + future)
- Feature maturity matrix
- Architecture evolution plan

## Dependencies
- 01-product (product direction)
- 06-architecture (architecture evolution)
- 38-refactoring (technical debt reduction)
- 39-future (long-term vision)

## Sequence: Phase Planning Flow
```
Stakeholder Input → Backlog Grooming → Phase Scope Definition → Kickoff → Implementation → Review → Release
```

## Completed Phases (11)
| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Foundation fixes (tsc/lint zero errors, hook deps, aliases) | ✅ |
| 1 | DB consolidation 26→12 tables, JSON bridge columns | ✅ |
| 2 | Seed data (authoritative seed_all.py), DB integrity | ✅ |
| 3 | Security & auth hardening, permission gates, headers | ✅ |
| 4 | Zero gradients — flat solid colors only | ✅ |
| 5 | i18n full coverage — no hardcoded Arabic in 33 files | ✅ |
| 6 | RTL visual polish — 200+ violations fixed, logical CSS | ✅ |
| 7 | Path engine — skill_ids fix, PUT/POST skills endpoints | ✅ |
| 8 | Assessment engine + analytics dashboard | ✅ |
| 9 | Performance — 11 indexes, 10 N+1 fixes, dynamic imports | ✅ |
| 10 | Project cleanup, docs, Lighthouse 100/100/100/100 | ✅ |
| 11 | DB normalization (junction tables), RBAC seed, admin fixes | ✅ |

## Phase 3 Architecture Future
| Phase | Focus | Status |
|-------|-------|--------|
| 3 | Adaptive learning, mastery tracking | Partially implemented (AEIS schema) |
| 4.0 | Ecosystem synchrony, project submissions | Services exist, not wired |
| 4.5 | Vector search, embeddings | VectorSearchService exists, not integrated |

## ERD References
- Roadmap tracks schema evolution (26→12 tables, junction tables, etc.)

## Rules
1. Each phase must have a clear scope definition
2. Phases must not introduce regressions in previous phases
3. Breaking changes require deprecation warning one phase prior
4. All phases must maintain Lighthouse 100/100/100/100

## Examples
- Phase 11 delivered: skill_categories, skill_prerequisites, job_role_skills, path_skills junction tables
- Phase 10 delivered: 100/100/100/100 Lighthouse, 0 CLS, updated docs

## Edge Cases
- Phase scope creep → extra features deferred to next phase
- Dependency between phases → sequential execution required
- Phase rollback on regression → revert and fix before proceeding

## Failure Cases
- Phase delivers incomplete features → blocked by test gates
- Phase causes performance regression → revert and re-optimize
- Phase documentation missing → blocked until written

## Recovery Procedures
1. Revert phase changes if regression detected
2. Re-scope remaining work to next phase
3. Update roadmap document with lessons learned

## Refactoring Strategy
- Roadmap reviewed quarterly with stakeholders
- Technical debt items prioritized alongside features
- Phases should be 2-4 weeks of work for predictability
