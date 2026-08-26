# SS-EDS: Clean Code

## Purpose
Document the clean code principles and practices adopted for SkillSynth development. Covers naming conventions, function size, single responsibility, DRY principle, and code review standards.

## Responsibilities
- Promote readable, maintainable code
- Enforce single responsibility principle
- Reduce code duplication (DRY)
- Encourage small, focused functions and components
- Document code quality expectations for PR reviews

## Inputs
- Clean Code principles (Robert C. Martin)
- Project-specific conventions (19-conventions)
- Team code review feedback

## Outputs
- Code quality guidelines
- PR review checklist
- Refactoring triggers

## Dependencies
- 19-conventions (coding conventions)
- 38-refactoring (refactoring patterns)
- 48-style-guide (style specifics)

## Sequence: Code Review Quality Check
```
Submit PR → Automated Checks (lint/type) → Readability Review → Structure Review → Test Coverage → Approve
                                              ↓                       ↓
                                         Request Changes       Request Refactor
```

## Principles
1. **Single Responsibility**: Each function/component does one thing
2. **DRY**: No code duplication — extract into shared utilities
3. **Small Functions**: Functions under 50 lines, components under 200 lines
4. **Meaningful Names**: Variables describe what they contain, functions describe what they do
5. **No Comments**: Code should be self-documenting; comments indicate code smell
6. **Early Return**: Guard clauses over nested if-else
7. **No Magic Numbers**: Named constants for all literal values
8. **Consistent Error Handling**: Services never throw, return fallbacks

## ERD References
- No clean-code specific tables

## Rules
1. Functions should not exceed 50 lines of logic
2. Components should not exceed 200 lines
3. No commented-out code in commits
4. No console.log in production code (use structured logging)
5. Imports must be organized: third-party → project → local
6. Files should not exceed 500 lines (split if larger)

## Examples
- Bad: `function processData(a, b, c) { /* 80 lines */ }`
- Good: `function calculateSkillLevel(skillScore: number): SkillLevel { /* 10 lines */ }`
- Bad: Component with 3 different responsibilities (fetch, render, animate)
- Good: Separate hook (usePathData) + Presentational component (PathCard) + Animation wrapper

## Edge Cases
- Legacy code that violates principles → refactor gradually
- Auto-generated code → may not follow clean code, note in comments
- Performance-optimized code → readability may suffer, document trade-off

## Failure Cases
- Unreviewed code with violations → caught in PR
- Growing technical debt → scheduled refactoring sprints
- Inconsistent naming across team → convention documentation

## Recovery Procedures
1. Run linter to catch style issues
2. Extract large functions into smaller ones
3. Remove duplicate code into shared utilities

## Refactoring Strategy
- Dedicated refactoring sprint every quarter
- Code quality metrics tracked in CI (complexity, duplication)
- Pair programming for complex refactoring
- Automated refactoring tools (Prettier, ESLint --fix)
