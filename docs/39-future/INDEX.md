# SS-EDS: Future

## Purpose
Record candidate future work for SkillSynth. Deliberately conservative: items are hypotheses until they have an ADR and a verification command. The system is feature-complete for its 15-table scope; growth should extend, not restore, removed features.

## Responsibilities
- Hold evaluated-but-unstarted ideas with entry criteria
- Prevent accidental reintroduction of removed capabilities (ADR-013)
- Link each item to the decision record that would authorize it

## Inputs
- Product feedback from demo users
- Operational friction observed in runbooks (42-runbooks)
- Dependency updates with breaking potential

## Outputs
- Prioritized candidate list
- Entry criteria per item

## Dependencies
- 29-roadmaps (active queue — only items promoted from here)
- 41-decision-records (ADR gate)

## Candidate List
| Candidate | Value | Entry criteria |
|-----------|-------|----------------|
| PostgreSQL cutover | Prod-grade persistence | MODE=prod deployment target exists; DDL port verified by tools/verify_schema.py against Postgres |
| CI pipeline | Automated pytest + builds on push | Runner available; suite stays green (<2 min) |
| Email service | Real password-reset delivery | SMTP provider chosen; reset flow keeps signed-token design |
| Export (CSV) of analytics | Admin reporting value | Key set frozen today; exporter pinned to documented keys |
| Path regeneration diffing | UX polish for regenerate flows | New endpoint + tests; no change to generation determinism |
| Docker Compose profile | One-command local stack | Existing Dockerfiles compose'd; health checks pass |

## Explicitly Not Planned (removed features stay removed — ADR-013)
Gamification (XP/levels/streaks/achievements), notifications center, sessions table, granular roles, vector search/embeddings, knowledge ingestion, any second push transport beside SSE. Reintroducing any requires a superseding ADR with evidence of demand.

## Sequence: Promotion Path
```
Candidate → spike/ADR draft → review vs 00-principles → accepted → scheduled in 29-roadmaps
                                  ↓ rejected → recorded as rejected option in the ADR
```

## Rules
1. No candidate starts coding before its ADR exists
2. Candidates must not widen the API surface beyond the router conventions in 07-backend
3. Any schema addition keeps strict 3NF and updates src/migrations/003_reduced_schema.sql + verifier
4. i18n parity is a release gate for any user-visible candidate

## Examples
- PostgreSQL cutover is config-driven today (MODE/DATABASE_URL in config/app_settings.py) — the work is verification, not code
- CSV export would read admin_service aggregates; no new tables needed

## Edge Cases
- Candidate conflicts with an existing ADR → it must supersede, not sidestep
- Candidate needs a third-party dependency → license + maintenance check first

## Failure Cases
- Scope creep via "small" candidates → enforce the ADR gate regardless of size

## Recovery Procedures
1. If a candidate stalls twice, close it with a short rationale note here

## Refactoring Strategy
- Review quarterly; delete stale candidates rather than maintaining dead intentions
