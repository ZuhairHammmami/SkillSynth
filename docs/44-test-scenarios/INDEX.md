# SS-EDS: Test Scenarios

## Purpose
Map the automated pytest suite to the behaviors it proves. The suite is the source of truth — 142 tests across 11 files, run against an isolated temp SQLite DB (tests/conftest.py); the dev DB is never touched. No manual-only scenarios are tracked here.

## Responsibilities
- Document what each suite file covers with representative scenarios
- State the execution and isolation model
- Point new work at the right file

## Inputs
- tests/ suite (pytest + httpx API client)
- Seeded temp DB built per session by tests/conftest.py (+ tests/integrity_support.py helpers)

## Outputs
- Green pipeline: `PYTHONPATH=src python -m pytest tests/ -q` → 142 passed

## Dependencies
- 16-testing (strategy, commands, coverage rules)
- 03-functional-requirements (behaviors under test)

## Suite Map
| File | Tests | Covers |
|------|-------|--------|
| tests/test_admin.py | 22 | Admin CRUD for users/skills/categories/resources/job-roles, events feed, backups |
| tests/test_catalog_integrity.py | 20 | Rename conflicts 409 (incl. case-insensitive), unknown-FK 400, self/ancestor cycles 400, restricted deletes + ?force=true |
| tests/test_catalog.py | 19 | Public catalog reads, wizard options, resource queries |
| tests/test_auth.py | 17 | Register/login, lockout 5→15min, me GET/PUT, change-password, reset flow, SSE token |
| tests/test_learning.py | 15 | Path generation, graph/gaps endpoints, step complete/undo, progress dashboard |
| tests/test_assessments.py | 13 | Question fetch, submit scoring → user_skills, role-based question sets |
| tests/test_integrity.py | 10 | Cascade matrix vs ERD contract, census payloads, duplicate natural keys 409/400, double-complete idempotence |
| tests/test_analytics.py | 8 | Dashboard keys, skill-growth, path-progress ownership, learning history/velocity |
| tests/test_schema.py | 7 | ORM ↔ DDL parity for the 15 tables (mirrors tools/verify_schema.py) |
| tests/test_realtime.py | 7 | SSE stream auth, connected/ping frames, publish gating |
| tests/test_learning_guards.py | 4 | Cross-user access 404, mastered-skill omission, topological step order, /generate alias parity |

## Representative Scenarios
```gherkin
Scenario: Restricted delete returns a census            # test_integrity.py
  Given a skill referenced by job-role mappings and path steps
  When an admin sends DELETE /api/admin/skills/{id}
  Then the response is 409 with detail.dependents counting every dependent
  When the same call is repeated with ?force=true
  Then dependents are removed per the ERD cascade contract and the response is 200

Scenario: Prerequisite cycle is rejected                # test_catalog_integrity.py
  Given skill A already depends on skill B
  When an admin PUTs B with prerequisite A
  Then the response is 400 naming the cycle before any write

Scenario: Lockout after repeated failures               # test_auth.py
  Given 5 consecutive wrong passwords for one account
  When a 6th login attempt arrives
  Then it is rejected and further attempts stay locked for 15 minutes

Scenario: Generated path respects mastery and order     # test_learning_guards.py
  Given assessment answers scoring some skills at level >= 3
  When POST /api/generate-path/ runs
  Then mastered skills are omitted and remaining steps follow topological order
```

## Rules
1. Every bug fix lands with a regression test in the matching file
2. New endpoint → at least one happy-path and one negative test before merge
3. Tests assert status codes AND payload shapes (census keys, dashboard keys)
4. Suite must stay hermetic: no network, no dev DB, deterministic seeds
5. Scenario docs update in the same PR as suite changes

## Examples
- Adding PUT /api/admin/resources/{id} semantics → extend tests/test_admin.py, not a new file

## Edge Cases
- IntegrityError-net behavior (409 after guard slip) covered by test_catalog_integrity.py::test_duplicate_junction_insert_returns_409
- DB usability post-conflict asserted by test_db_still_usable_after_conflict

## Failure Cases
- Flaky ordering issues → conftest rebuilds schema; never rely on cross-file state

## Recovery Procedures
1. Run the single failing file first: PYTHONPATH=src python -m pytest tests/test_<file>.py -q
2. Bisect with -k "test_name_fragment"

## Refactoring Strategy
- Keep files grouped by router concern; split only when a file approaches the 300-line limit
