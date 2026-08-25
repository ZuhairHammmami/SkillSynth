# SS-EDS: Product

## Purpose
Define the SkillSynth product as an adaptive learning operating system with a modular synthesizer metaphor. Covers value proposition, target users, core features, and product roadmap.

## Responsibilities
- Maintain product vision and feature catalog
- Define user personas (learner, manager, admin)
- Track phase completion (11 phases complete as of Phase 11)
- Document feature toggles and maturity levels

## Inputs
- Stakeholder requirements
- Competitive analysis
- User research on adaptive learning platforms

## Outputs
- Product feature registry
- Persona definitions
- Phase roadmap (docs/45-release-notes/)
- Feature maturity matrix

## Dependencies
- 02-business (monetization)
- 29-roadmaps (product timelines)
- 00-principles (design philosophy constrains product)

## Sequence: Feature Lifecycle
```
Idea → RFC → Kickoff → Implementation → Beta → GA → Sunset
         ↓
  Product Review Board
         ↓
  Approved / Rejected
```

## State Diagram: Phase Completion
```
Phase 0 (Foundation)    → [Complete] Phase 1 (DB Consolidation)
  → Phase 2 (Seed)      → Phase 3 (Auth) → Phase 4 (Gradients)
  → Phase 5 (i18n)       → Phase 6 (RTL) → Phase 7 (Path Engine)
  → Phase 8 (Assessment)  → Phase 9 (Performance) → Phase 10 (Cleanup)
  → Phase 11 (Normalization, RBAC, Audit)
```

## ERD References
- docs/10-database/ for product data entities
- docs/40-diagrams/UML_USECASE.md

## Rules
- No feature ships without i18n coverage
- All features must work in RTL first
- Every feature must have an admin management path
- Feature must have analytics tracking from day one

## Examples
- Phase 11 features: DB normalization (junction tables), RBAC seed, wizard restructure, real-time audit log

## Edge Cases
- Free tier vs. premium feature gating
- Offline capability for learning paths
- Multi-tenant isolation (future)

## Failure Cases
- Feature ships without i18n → blocked by Phase 5 gate
- Feature breaks Lighthouse 100/100/100/100 → revert

## Recovery Procedures
1. Rollback feature flag
2. File hotfix PR with required i18n/analytics
3. Retroactive audit (docs/42-runbooks/)

## Refactoring Strategy
- Product features are independently flag-gated for gradual rollout
- Deprecated features get a 2-phase removal (soft warning → hard removal)
- Quarterly product health review against KPIs
