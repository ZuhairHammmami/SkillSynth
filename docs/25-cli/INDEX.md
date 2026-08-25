# SS-EDS: CLI — DEPRECATED

> **⚠️ CLI tool removed.** Standalone `tools/cli/` package deleted. Script commands below remain in AGENTS.md for reference.

## Purpose
Document the command-line interface tools and scripts available for SkillSynth development, seed, and verification tasks.

## Responsibilities
- Maintain CLI scripts for common development tasks
- Provide seed, verification, and admin management commands
- Document proper usage and expected outputs

## Inputs
- Developer workflow requirements
- Automation needs (seeding, testing, admin creation)

## Outputs
- CLI scripts documentation
- Usage examples and expected outputs

## Dependencies
- 07-backend (Python scripts)
- 08-frontend (TypeScript scripts)
- 10-database (seed scripts)

## CLI Commands Reference
| Command | Purpose | Working Dir |
|---------|---------|-------------|
| `python run.py` | Start FastAPI backend (port 8000) | Root |
| `pnpm dev` | Start Next.js dev server (port 3000) | src/frontend |
| `pnpm build` | Build frontend (tsc + next build) | src/frontend |
| `pnpm type-check` | TypeScript strict check | src/frontend |
| `pnpm lint` | ESLint check | src/frontend |
| `python seed_all.py` | Full DB seed | Root |
| `npx ts-node src/scripts/test-path-resolver.ts` | Test DAG logic | Root |
| `npx ts-node src/scripts/test-ui-rendering.ts` | Test UI rendering | Root |
| `npx ts-node src/scripts/test-notification-loop.ts` | Test notifications | Root |
| `npx ts-node src/scripts/test-db-connection.ts` | Test DB connection | Root |
| `python src/backend/create_admin.py` | Create admin user | Root |

## Sequence: CLI Command Resolution
```
User Command → Shell → Working Directory Check → Script Path Resolution → Execute → Output
```

## Seed Scripts
| Script | Tables Seeded | When |
|--------|---------------|------|
| python seed_all.py | All 12+ tables | First setup, DB reset |
| python src/scripts/seed.py | Minimal (2 categories, 6 skills, 1 role) | PostgreSQL testing |
| npx ts-node src/scripts/seed-engineering-path.ts | Engineering path DAG | Phase 3 testing |

## ERD References
- seed_all.py populates all database tables

## Rules
1. Always run from correct working directory (AGENTS.md specifies for each command)
2. seed_all.py is idempotent — checks existing_skills_count > 0 before seeding
3. Python scripts use `PYTHONPATH=src` prefix when running directly
4. TypeScript scripts use `npx ts-node` for execution

## Examples
```bash
# Start backend
python run.py

# Seed database
python seed_all.py

# TypeScript check
cd src/frontend && pnpm type-check
```

## Edge Cases
- Python path issues when running from wrong directory
- Node modules not installed for ts-node scripts
- seed_all.py partially completed on failure

## Failure Cases
- `python run.py` fails due to missing dependencies
- `pnpm dev` fails due to port conflict
- seed script fails due to database connection issue
- ts-node script fails due to TypeScript compilation error

## Recovery Procedures
1. Verify correct working directory
2. Install dependencies: `pip install -r requirements.txt` / `pnpm install`
3. Check port availability (8000 for backend, 3000 for frontend)
4. Delete DB file and re-run seed

## Refactoring Strategy
- Add a unified CLI tool (e.g., `skill-synth-cli`) with subcommands
- Migrate from ts-node to built JavaScript for script execution
- Add argument parsing and help text for all scripts
