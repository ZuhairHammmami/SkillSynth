# Coding Standards

## Python (Backend)
| Rule | Standard |
|------|----------|
| Format | Black (default config), line length 120 |
| Imports | `from backend.xxx import yyy` (never `src.backend`) |
| Type Hints | Required for all function signatures |
| Docstrings | Google style for all public functions |
| File Size | Maximum 300 lines |
| Function Size | Maximum 40 lines |
| Classes | Single responsibility, max 200 lines |
| Naming | snake_case functions/vars, PascalCase classes, UPPER_CASE constants |

## TypeScript (Frontend)
| Rule | Standard |
|------|----------|
| Format | Prettier (default config) |
| Imports | Absolute imports via `@/` (mapped to `src/`) |
| Types | Strict mode, explicit types, no `any` |
| Components | PascalCase files, default export |
| Hooks | camelCase, `use` prefix, named export |
| File Size | Maximum 250 lines |
| Function Size | Maximum 40 lines |

## SQL
| Rule | Standard |
|------|----------|
| Naming | snake_case tables/columns |
| Joins | Explicit JOIN syntax (no implicit) |
| Indexes | Index all FK columns and frequently queried columns |
| Migrations | Alembic (once fully migrated) |

## General
- No circular imports
- No dead code (unused imports, variables, functions)
- No `TODO` or `FIXME` without tracking in issue tracker
- All PRs must pass: type-check → lint → test → build
