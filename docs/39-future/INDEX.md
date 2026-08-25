# SS-EDS: Future

## Purpose
Document the long-term vision and planned future enhancements for SkillSynth beyond the current 11 completed phases. Covers adaptive learning, ecosystem synchrony, vector search, and architectural evolution.

## Responsibilities
- Maintain future vision document
- Track planned but unimplemented features
- Document architectural evolution targets
- Identify integration opportunities (Supabase, LLM, vector search)

## Inputs
- Product roadmap
- Technical feasibility assessments
- Market trends in adaptive learning

## Outputs
- Future feature specifications
- Phase 3+ architecture plans
- Integration roadmap

## Dependencies
- 29-roadmaps (completed phases)
- 06-architecture (current architecture)
- 01-product (future product direction)

## Sequence: Future Feature Adoption
```
Research → Prototype → Alpha → Beta → GA → Post-GA Improvements
```

## Future Initiatives
| Initiative | Priority | Status | Dependencies |
|------------|----------|--------|--------------|
| AEIS Schema Integration | High | Partially implemented | database migration 001-005 |
| Supabase Auth Integration | Medium | Not started | @supabase/ssr installed |
| Vector Search | Medium | Service exists, not wired | pgvector, embedding pipeline |
| Project Submissions | Low | Stubbed | Storage, validation |
| Adaptive Learning (mastery) | High | Partially implemented | AEIS, assessment engine |
| Ecosystem Synchrony | Low | Services exist, not wired | Notification, conflict checker |
| Docker Compose Setup | Medium | Not started | Deployment infrastructure |
| Test Framework Integration | High | Not started | Vitest, pytest, Playwright |
| CI/CD Pipeline Fix | High | Broken | Workflow files |
| Mobile App (React Native) | Low | Not started | Full API layer |

## Technical Debt for Future
| Item | Impact | Effort |
|------|--------|--------|
| No test framework | High | Large |
| Broken CI/CD | High | Medium |
| No HttpOnly cookie | Medium | Small |
| No token blacklist | Medium | Medium |
| Next.js API routes stubbed | Medium | Large |
| Static JSON vs DB overlap | Low | Medium |

## ERD References
- AEIS schema: src/migrations/001-005.sql
- Future schema changes will maintain backward compat

## Rules
1. Future features must not break existing functionality
2. All new features must include i18n from day one
3. Performance budget must be maintained for new features
4. Security review required for all new integrations
5. Deprecation period of at least one phase for removed features

## Examples
- Vector Search: implemented in VectorSearchService.ts (463 lines), generates embeddings via local/Ollama or OpenAI, searches pgvector cosine distance
- Project Submission: ProjectSubmissionService.ts (327 lines), stubbed

## Edge Cases
- Future feature conflicts with current architecture → ADR required
- Third-party API (Supabase) becomes incompatible → abstraction layer
- LLM provider pricing changes → hybrid strategy mitigates

## Failure Cases
- Feature never completed due to scope → document for next phase
- Integration breaks existing features → regression tests catch
- Technology becomes obsolete → plan migration early

## Recovery Procedures
1. Review feature against current architecture compatibility
2. Check dependencies for breaking changes
3. Update roadmap with revised timeline

## Refactoring Strategy
- Future features are independently flag-gated
- Each feature has a dedicated RFC/ADR
- Quarterly review of future roadmap against market changes
- Regular dependency updates to prevent technical lock-in
