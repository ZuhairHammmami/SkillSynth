# SS-EDS: Style Guide

## Purpose
Document the coding style guide for SkillSynth, covering language-specific formatting rules, naming conventions, and linting configuration.

## Responsibilities
- Define and enforce code formatting rules
- Maintain ESLint configuration
- Document naming conventions for all languages
- Provide formatting examples

## Inputs
- TypeScript/React best practices
- Python PEP 8 guidelines
- Project conventions (19-conventions)

## Outputs
- Style guide document
- ESLint rules
- Prettier configuration (future)

## Dependencies
- 19-conventions (general conventions)
- 37-clean-code (code quality)

## Sequence: Style Enforcement
```
Developer → Write Code → Format (Prettier future) → Lint (ESLint) → Fix Issues → Commit
```

## TypeScript/React Style
- **Components**: PascalCase (e.g., `PathCard`, `StepItem`)
- **Functions**: camelCase (e.g., `fetchPaths`, `completeStep`)
- **Hooks**: `use*` prefix (e.g., `usePaths`, `useAuth`)
- **Files**: Component files match component name
- **Props**: TypeScript interface with `interface ComponentNameProps`
- **Imports**: Third-party → @ alias → relative
- **Strings**: Single quotes preferred
- **Semicolons**: Required

## Python Style (PEP 8)
- **Snake case**: `get_current_user`, `create_admin_user`
- **Classes**: PascalCase (e.g., `ProfileCreate`, `PathResponse`)
- **Max line length**: 120 characters
- **Imports**: Standard library → Third-party → Local
- **Type hints**: Required on all function signatures
- **Docstrings**: Google-style for public functions

## CSS/Tailwind Style
- **Custom properties**: Kebab-case (`--bg-root`, `--font-body`)
- **Tailwind classes**: Utility-first approach
- **Dark mode**: `darkMode: ["class"]` — dark-only theme
- **Responsive**: Mobile-first breakpoints
- **Animations**: Explicit properties only (no `transition: all`)

## ERD References
- No style-specific database tables

## Rules
1. No Prettier currently configured (future improvement)
2. ESLint extends next/core-web-vitals
3. Python: no formatter configured (pyproject.toml missing)
4. CSS: no gradients, no soft shadows, no glassmorphism
5. RTL: logical properties over physical (ms-/me- not ml-/mr-)

## Examples
- Good TSX: `export function PathCard({ path }: PathCardProps) { ... }`
- Good Python: `def get_current_user(token: str = Depends(oauth2_scheme)) -> Profile:`
- Bad: `function getData(){...}` — should be descriptive

## Edge Cases
- File with both TypeScript and Python → follow language-specific rules
- Legacy code not matching style → format on modification
- Auto-generated code → may not match style, acceptable exception

## Failure Cases
- Style violation in PR → ESLint catches (TypeScript) or review catches (Python)
- Missing linter for Python → manual review required
- Inconsistent formatting → Prettier needed

## Recovery Procedures
1. Run ESLint with --fix for auto-correction
2. Manually fix remaining style issues
3. Add Prettier configuration (future)

## Refactoring Strategy
- Add Prettier for consistent formatting
- Configure Python linter (ruff or flake8) in pyproject.toml
- Add pre-commit hooks for auto-formatting
- Enforce style guide in CI pipeline
