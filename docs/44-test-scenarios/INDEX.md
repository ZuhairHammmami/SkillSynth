# SS-EDS: Test Scenarios

## Purpose
Document test scenarios for critical system behaviors in SkillSynth. Provides manual test cases that can be executed to verify system functionality before automated tests are implemented.

## Responsibilities
- Define manual test scenarios for key features
- Document expected behaviors and edge cases
- Provide step-by-step test instructions
- Track scenario coverage across features

## Inputs
- Feature specifications
- Bug reports
- User feedback

## Outputs
- Test scenario documents
- Expected behavior specifications
- Edge case coverage

## Dependencies
- 16-testing (test strategy)
- 03-functional-requirements (testable requirements)
- 05-domain (domain rules to verify)

## Sequence: Manual Test Execution
```
Select Scenario → Setup Prerequisites → Execute Steps → Compare Result with Expected → Pass/Fail → Report
```

## Test Scenario: Path Generation
```gherkin
Scenario: Generate personalized learning path
  Given user has completed assessment
  When user submits POST /api/generate-path/ with goal, answers, preferences
  Then system returns path with ordered steps
  And path steps have prerequisite-respecting order
  And mastered skills (level ≥ 3) are skipped
  And resources are assigned matching language preference
```

## Test Scenario: Step Completion Gamification
```gherkin
Scenario: Complete step awards XP and updates streak
  Given user has 0 XP and streak_count=0
  When user completes step via POST /api/steps/{step_id}/complete
  Then user XP becomes 10
  And streak_count becomes 1
  And last_activity_date is today
  And SSE event step_completed is fired
```

## Test Scenario: RBAC Permission Enforcement
```gherkin
Scenario: Non-admin cannot access admin endpoints
  Given user is authenticated with role "student"
  When user sends GET /api/admin/users
  Then system returns 403 Forbidden
```

## ERD References
- All tables are involved in test scenarios

## Rules
1. Each functional requirement must have at least one test scenario
2. Scenarios use Gherkin-like format (Given/When/Then)
3. Edge cases must have dedicated scenarios
4. Scenarios must specify prerequisites
5. Failure scenarios must be documented alongside success

## Examples
- Path generation with empty skill profile (all skills new)
- Path generation with all skills mastered (empty path)
- Step completion with concurrent requests
- Admin deletion of own account (should fail)

## Edge Cases
- Network interruption during assessment submission
- Database connection loss during path generation
- ~~Concurrent gamification updates from multiple tabs~~ (gamification removed)

## Failure Cases
- Test scenario fails → log bug with reproduction steps
- Test scenario outdated → update with feature changes
- Scenarios not covering new feature → add before release

## Recovery Procedures
1. Reproduce issue following test scenario
2. Identify root cause from failure
3. Fix and verify against same scenario

## Refactoring Strategy
- Convert manual scenarios to automated tests
- Add scenario coverage tracking
- Implement scenario-based testing framework
