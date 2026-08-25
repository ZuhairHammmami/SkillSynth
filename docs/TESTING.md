# Testing — DEPRECATED (absorbed into SS-EDS docs/16-testing/)

> **⚠️ `CLI tool` row — CLI tool removed.** & Verification

## Current State: No Test Framework

**No Jest, Vitest, pytest, or any test runner is configured** anywhere in the project.

| Component | Tests Exist? | Details |
|-----------|-------------|---------|
| Python backend | ❌ | No `conftest.py`, no `test_*.py` files, no `pytest` in requirements |
| TypeScript frontend | ❌ | No `jest.config`, `vitest.config`, `*.test.ts`, or `*.spec.ts` files |
| CLI tool | ❌ | No test libraries in `tools/cli/package.json` |
| CI/CD | 🚫 Broken | `.github/workflows/ci.yml` uses wrong paths (`./frontend` not `./src/frontend`, `./backend` not `.`) and wrong package manager (`npm` not `pnpm`) |

## Manual Test Scripts

```bash
# Path resolver DAG logic (3 scenarios: partial, blocked, complete)
npx ts-node src/scripts/test-path-resolver.ts

# Mastery page UI rendering (generates HTML snapshots)
npx ts-node src/scripts/test-ui-rendering.ts

# Notification/validation logic (Zod validation, API responses, toast, admin alerts)
npx ts-node src/scripts/test-notification-loop.ts

# Supabase connectivity + RLS check
npx ts-node src/scripts/test-db-connection.ts
```

## Verification Commands (some missing)

```bash
# Working:
cd src/frontend && pnpm type-check      # tsc --noEmit
cd src/frontend && pnpm lint            # next lint (ESLint)
cd src/frontend && pnpm build           # type-check + next build

# Documented but DO NOT EXIST (FIXME):
python verify-db-setup.py               # Does not exist
bash verify-aeis-setup.sh               # Does not exist
bash verify-phase2-neural-operation.sh  # Does not exist
```

## What To Test & When

| When | Command | Purpose |
|------|---------|---------|
| Before any frontend commit | `pnpm type-check` | TypeScript strict mode |
| Before any frontend commit | `pnpm lint` | ESLint (next/core-web-vitals) |
| Before merge to main | `pnpm build` | Full type-check + production build |
| After backend changes | `python run.py` (manual) | Verify dev server starts |
| After DB changes | `python seed_all.py` | Verify seeding works |
| After path gen changes | `npx ts-node .../test-path-resolver.ts` | Verify DAG logic |
| After UI changes | `npx ts-node .../test-ui-rendering.ts` | Verify mastery page |
| After Supabase config | `npx ts-node .../test-db-connection.ts` | Verify connectivity |

## Known Gaps

1. **No unit tests** — zero coverage for any module
2. **No integration tests** — no API-level testing
3. **No E2E tests** — no Playwright/Cypress
4. **4 verification scripts missing** — documented but not created
5. **CI is broken** — wrong paths, wrong package manager, references non-existent `flake8` config
6. **No Python linter configured** — `pyproject.toml` has no flake8/ruff/black section
7. **No Prettier** — no code formatter anywhere
8. **No pre-commit hooks** — no husky/lint-staged

## VS Code Test Config

From `.vscode/settings.json`:
```json
{
  "python.testing.unittestArgs": ["-v", "-s", ".", "-p", "*test.py"],
  "python.testing.pytestEnabled": false,
  "python.testing.unittestEnabled": true
}
```
Uses `unittest` (not pytest), matching `*test.py` files in workspace root.
Only useful once test files actually exist.
