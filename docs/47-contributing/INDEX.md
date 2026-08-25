# SS-EDS: Contributing

> **Source**: References AGENTS.md guide and CONTRIBUTING.md (Arabic PR template)

## Purpose
Document the contribution guidelines for SkillSynth, covering PR process, coding standards, commit conventions, and team workflows.

## Responsibilities
- Define contribution workflow
- Document PR submission and review process
- Maintain coding standards for contributors
- Provide onboarding guide for new developers

## Inputs
- AGENTS.md conventions
- PR template (Arabic)
- Team workflow agreements

## Outputs
- Contribution guidelines
- PR template
- Onboarding checklist

## Dependencies
- 19-conventions (coding conventions)
- 37-clean-code (code quality)
- 43-checklists (PR checklist)

## Sequence: Contribution Flow
```
Fork/Clone → Create Branch → Implement → Commit (Conventional) → Push → Create PR → Review → Address Feedback → Merge → Delete Branch
```

## PR Requirements
1. Conventional commit message: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`
2. PR template in Arabic per existing standard
3. TypeScript: zero tsc errors
4. ESLint: zero errors (documented warnings OK)
5. Build: `pnpm build` passes
6. i18n: all new text uses t() function, both locale files updated
7. RTL: logical CSS properties used (ms-/me-, ps-/pe-)
8. Performance: no N+1 queries, bundle size OK

## Development Environment
```bash
# Backend
source .venv/bin/activate
pip install -r requirements.txt
python run.py

# Frontend
cd src/frontend
pnpm install
pnpm dev
```

## ERD References
- No contribution-specific database tables

## Rules
1. Never commit to main branch directly
2. Branch naming: feat/description, fix/description, refactor/description
3. PR description must be in Arabic (per existing template)
4. PR requires at least one reviewer approval
5. No commits without explicit user request (agentic workflow)

## Examples
- Good commit: `feat(paths): add PUT /paths/{id}/skills endpoint`
- Good PR description: Arabic text following template format

## Edge Cases
- Urgent hotfix → expedited review with post-merge verification
- External contributor → provide detailed onboarding guide
- Large PR → split into multiple smaller PRs

## Failure Cases
- PR without tests → blocked (until tests exist)
- PR with lint errors → CI fails
- PR with missing i18n → caught in review

## Recovery Procedures
1. Fix lint/type errors and force push
2. Address review comments in follow-up commits
3. Rebase to resolve merge conflicts

## Refactoring Strategy
- Automate contribution checks in CI
- ~~Create contribution template CLI~~ (CLI tool removed)
- Document common contribution scenarios
- Maintain contributing guide alongside code changes
