# SS-EDS: Conventions

> **Source**: Migrated from AGENTS.md conventions section

## Purpose
Document coding standards, naming conventions, import patterns, commit message format, and development workflow conventions for the SkillSynth project.

## Responsibilities
- Define and enforce coding conventions
- Maintain import patterns (Python, TypeScript)
- Document commit message format (Conventional Commits)
- Set branch naming and PR conventions

## Inputs
- Industry best practices
- Project team agreements
- Language-specific style guides (PEP 8, Prettier)

## Outputs
- Coding standards document
- Lint rules (ESLint, future Ruff/flake8)
- Commit message templates
- PR template

## Dependencies
- 00-principles (philosophical foundation)
- 48-style-guide (specific style rules)
- 37-clean-code (code quality)
- 38-refactoring (refactoring patterns)

## Sequence: Code Review Convention Check
```
Submit PR → Automated Lint Check → Convention Review → Human Review → Approved → Merge
                ↓ Fail                         ↓ Fail
            Fix Issues                   Request Changes
```

## State Diagram: Commit Lifecycle
```
[Working] → `git add` → [Staged] → `git commit` → [Committed] → `git push` → [Remote]
                                                    ↓
                                              Pre-commit hooks
                                                    ↓
                                              Pass/Fail
```

## Python Conventions
1. Imports: `from backend import X` (not `from src.backend`)
2. run.py injects src/ into sys.path
3. Type hints required on all function signatures
4. Pydantic models for all request/response schemas
5. SQLAlchemy session managed via dependency injection

## TypeScript Conventions
1. Strict mode enabled in tsconfig.json
2. Path alias: `@/*` maps to `./src/*`
3. Service alias: `@/services/*` → `../services/*`
4. React components: PascalCase, functions: camelCase
5. Custom hooks: `use*` naming

## Git Conventions
1. Conventional Commits: feat:, fix:, docs:, style:, refactor:, test:
2. Branch naming: feat/description, fix/description, refactor/description
3. PR description in Arabic per template (AGENTS.md)
4. No commits without explicit user request

## ERD References
- No convention-specific tables

## Rules
1. Zero tsc errors mandatory
2. Zero ESLint errors (warnings OK if documented in AGENTS.md)
3. No hardcoded Arabic strings — always use i18n t()
4. No gradients anywhere in CSS
5. RTL-first: logical properties over physical
6. No box-shadow with blur > 0

## Examples
- Good: `import { usePaths } from '@/features/paths/hooks'`
- Bad: `import { usePaths } from '../../features/paths/hooks'`
- Good: `from backend import models`
- Bad: `from src.backend import models`

## Edge Cases
- Conflict between prettier and eslint rules
- Mixing Python and TypeScript conventions in the same file
- Legacy code that doesn't follow current conventions

## Failure Cases
- Import from wrong path → runtime ModuleNotFoundError
- Missing type hint → TypeScript strict error
- Conventional commit format violation → CI rejects

## Recovery Procedures
1. Run linter to auto-fix formatting issues
2. Review import paths against convention docs
3. Rebase to fix commit message format

## Refactoring Strategy
- Gradually migrate legacy code to current conventions
- Add automated convention checking in CI
- Document exceptions with clear rationale in AGENTS.md
