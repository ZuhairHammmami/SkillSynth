# SS-EDS: Refactoring

## Purpose
Document the refactoring strategy for SkillSynth, covering technical debt management, migration patterns, and code improvement initiatives across all phases.

## Responsibilities
- Identify and prioritize technical debt items
- Plan and execute refactoring initiatives
- Track refactoring progress across phases
- Ensure backward compatibility during migrations

## Inputs
- Code quality metrics
- Phase completion data
- Performance profiling
- Developer feedback

## Outputs
- Refactoring roadmaps
- Migration strategies
- Deprecation notices

## Dependencies
- 37-clean-code (principles to follow)
- 29-roadmaps (phase planning)
- 49-module-boundaries (architecture guidance)

## Sequence: Refactoring Process
```
Identify Debt → Prioritize → Plan → Implement → Test → Verify No Regression → Ship
```

## State Diagram: Code Quality Lifecycle
```
[Good] → [Technical Debt Accumulates] → [Refactoring Needed] → [Scheduled] → [Refactored] → [Good]
```

## Completed Refactoring Initiatives (Phase 0-11)
| Refactoring | Phase | Impact |
|-------------|-------|--------|
| DB consolidation 26→12 tables | 1 | Reduced complexity |
| JSON bridge columns → junction tables | 11 | Normalized schema |
| N+1 query fixes (10 instances) | 9 | Performance improvement |
| Gradient removal (flat colors) | 4 | Design consistency |
| RTL violations fixed (200+) | 6 | Layout correctness |
| Hardcoded Arabic → i18n | 5 | Localization coverage |
| Hook dependency fixes | 0 | Bug prevention |
| Dynamic imports for heavy components | 9 | Bundle size reduction |
| 11 composite indexes added | 9 | Query performance |

## Refactoring Patterns
1. **Strangler Fig Pattern**: Gradually replace legacy code while maintaining API compat
2. **Extract Method/Component**: Split large functions into smaller ones
3. **Replace Conditional with Polymorphism**: Clean complex conditionals
4. **Introduce Parameter Object**: Reduce function parameter count
5. **Separate Query from Modifier**: CQRS for data access

## ERD References
- Schema migration tracking in version control

## Rules
1. Always maintain backward compatibility during refactoring
2. Deprecation first, removal later (2-phase process)
3. Refactoring should not change external behavior
4. Each refactoring must have tests verifying no regression
5. Large refactorings split into multiple small PRs

## Examples
- JSON bridge columns → junction tables: old columns kept as deprecated, new junction tables added, data migrated in seed
- Static JSON → DB: both sources maintained during migration, DB preferred

## Edge Cases
- Refactoring introduces regression → revert and fix
- Third-party dependency refactoring → lock version, update at planned pace
- Database migration failure → rollback and fix

## Failure Cases
- Refactoring scope too large → never completed (split into phases)
- Refactoring changes behavior → tests catch regression
- Refactoring without tests → risky, deferred

## Recovery Procedures
1. Revert refactoring changes
2. Break refactoring into smaller steps
3. Add tests before refactoring

## Refactoring Strategy
- 20% of each sprint allocated to refactoring
- Technical debt tracked in issue tracker
- Refactoring candidates identified by code complexity metrics
- Major refactoring planned as dedicated phases
