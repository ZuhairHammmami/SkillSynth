# SS-EDS: Release Notes

## Purpose
Document release history and version tracking for SkillSynth. Covers all 11 completed phases, their scope, and deliverables.

## Responsibilities
- Maintain release history log
- Document phase scope and deliverables
- Track breaking changes and migration instructions
- Provide version compatibility matrix

## Inputs
- Phase completion reports
- Breaking change notices
- Migration scripts

## Outputs
- Release notes for each phase
- Migration guides
- Version compatibility documentation

## Dependencies
- 29-roadmaps (phase tracking)
- 38-refactoring (migration guidance)
- 01-product (feature releases)

## Sequence: Release Process
```
Code Freeze → QA Testing → Bug Fixing → Final Build → Deploy → Post-Deploy Monitoring
```

## Completed Releases
### Phase 11 — DB Normalization & RBAC
- **Date**: Current cycle
- **Scope**: Junction tables, RBAC seed, wizard restructure, path editing, real-time audit log, analytics improvements
- **Breaking**: Yes — schema migration (junction tables replace JSON bridge columns)
- **Migration**: Run seed_all.py to populate junction tables

### Phase 10 — Project Cleanup & Docs
- **Date**: Previous cycle
- **Scope**: ERD/UML diagrams, Lighthouse 100/100/100/100, docs/ cleanup
- **Breaking**: No
- **Migration**: None

### Phase 9 — Performance
- **Date**: Previous cycle
- **Scope**: 11 indexes, 10 N+1 fixes, dynamic imports, bundle optimization
- **Breaking**: No
- **Migration**: Re-run seed for indexes

### Phase 8 — Assessment Engine & Analytics
- **Date**: Previous cycle
- **Scope**: DB-backed assessments, submission scoring, analytics dashboard, skill growth tracking
- **Breaking**: No
- **Migration**: Run seed_all.py for assessment data

## Release Format
```markdown
## Phase X — Title
**Date**: YYYY-MM-DD
**Status**: Released | In Progress | Planned

### Scope
- Feature 1
- Feature 2

### Breaking Changes
- Migration step required

### Migration
```bash
python seed_all.py
```
```

## ERD References
- Database schema evolves across releases
- Seed_all.py ensures backward compatibility

## Rules
1. Each release must have a version number or phase identifier
2. Breaking changes must be clearly documented
3. Migration instructions must be provided for breaking changes
4. Each release must include i18n updates
5. Lighthouse score must not regress

## Examples
- Phase 11: 4 new junction tables created, seed_all.py populates from old JSON columns
- Phase 10: No schema changes, pure cleanup and documentation

## Edge Cases
- Skipped phase → document as "Not applicable"
- Partial release → document deployed subset
- Hotfix release → patch version increment

## Failure Cases
- Release without documentation → blocked by quality gates
- Release note inaccurate → developer confusion
- Breaking change not documented → production incident

## Recovery Procedures
1. Add missing release notes retroactively
2. Update inaccurate release information
3. Document lessons learned for future releases

## Refactoring Strategy
- Automate release note generation from commit history
- Link release notes to ADRs and migration scripts
- Create changelog comparison tool
