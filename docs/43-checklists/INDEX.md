# SS-EDS: Checklists

## Purpose
Provide development, deployment, review, and release checklists for SkillSynth to ensure consistency and completeness across all operations.

## Responsibilities
- Maintain pre-commit checklist
- Provide PR review checklist
- Document release checklist
- Track post-deployment verification checklist

## Inputs
- Common issues discovered during development
- Code review feedback patterns
- Deployment experience

## Outputs
- Actionable checklists for developers
- Quality gates for PRs and releases

## Dependencies
- 16-testing (verification steps)
- 17-deployment (deployment steps)
- 42-runbooks (operational procedures)

## Pre-Commit Checklist
- [ ] `pnpm type-check` passes (tsc --noEmit, 0 errors)
- [ ] `pnpm lint` passes (0 errors, documented warnings OK)
- [ ] No hardcoded Arabic strings (uses t() function)
- [ ] No N+1 queries introduced
- [ ] RTL logical properties used (ms-/me-, ps-/pe-)
- [ ] No gradients or soft shadows added
- [ ] Lighthouse 100/100/100/100 verified
- [ ] i18n keys added to both en.json and ar.json

## PR Review Checklist
- [ ] Code follows clean code principles (37-clean-code)
- [ ] No commented-out code
- [ ] Error states handled (loading, empty, error, edge cases)
- [ ] Mobile responsive (check <768px breakpoint)
- [ ] Keyboard navigable (Tab, Enter, Escape)
- [ ] ARIA labels present on interactive elements
- [ ] TypeScript strict mode satisfied
- [ ] Conventional commit format used
- [ ] PR description in Arabic (per template)

## Release Checklist
- [ ] All tests pass (type-check, lint, build)
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] CORS origins updated for new domains
- [ ] Lighthouse audit passed (100/100/100/100)
- [ ] Security headers configured for production
- [ ] Rate limiting configured for production
- [ ] Secret keys rotated (SECRET_KEY, API keys)
- [ ] Admin account verification
- [ ] Monitoring and alerting configured

## ERD References
- No checklist-specific database tables

## Rules
1. Checklists must be actionable (binary: done/not done)
2. Checklists live in version control alongside code
3. Checklists are reviewed and updated quarterly
4. Automated checks should replace manual checklist items

## Examples
- Pre-commit checklist is run before every commit
- Release checklist is run before every production deployment

## Edge Cases
- Checklist item not applicable → skip with justification
- New checklist items added during incident → documented for future
- Checklist automation in CI replaces manual verification

## Failure Cases
- Checklist item missed → caught in code review
- Checklist not updated for new technology → gaps
- Checklist too long → developers skip it

## Recovery Procedures
1. Review missed checklist items
2. Update checklist with lessons learned
3. Automate checklist items where possible

## Refactoring Strategy
- Convert checklist items into automated CI checks
- Add checklist verification as pre-commit hooks
- Create release checklist as CI pipeline stages
