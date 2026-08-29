# Changelog

All notable changes to SkillSynth are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/) and semantic versioning.

## [1.0.0] - 2026-08-29

### Added
- **Per-skill path generation** — `POST /api/generate-path/skill/{id}` generates a
  learning path for a single skill, reusing the prerequisite topological ordering
  and persistence flow; duplicate/mastered guard returns 409.
- **Learner catalog browsing** — `GET /api/catalog/skills/{id}` (skill detail with
  prerequisite/recommended strips) and `GET /api/catalog/roles` (lean role list).
- **SvelteKit catalog page** — three-state browser (categories → category skills →
  skill detail) with client-side mastered detection, duplicate-guard, and a
  `RecommendedStrip` component. Bilingual AR/EN with 709 i18n keys parity.
- **Production container images** — SvelteKit adapter-node Dockerfiles for the
  frontend app and the (new) admin app; SQLite persistence fixed via a directory
  volume. Configurable `DB_PATH` for the backend SQLite database.
- **CHANGELOG** — this file.
- Seed script updated to `seed_v4.py`.

### Changed
- Version bumped to `1.0.0` (backend `pyproject.toml`, frontend & admin `package.json`).
- Removed SvelteKit build artifacts (`.svelte-kit/`, `build/`) from version control
  and added them to `.gitignore`/`.dockerignore` across the repo.
- `.env.example` reordered to lead with the zero-config SQLite dev path; PostgreSQL,
  SendGrid, and Redis moved into a commented production section.
- Root and per-app Dockerfiles switched from Next.js to SvelteKit adapter-node;
  environment variable renamed from `NEXT_PUBLIC_API_BASE_URL` to `PUBLIC_API_BASE_URL`.

### Fixed
- Cross-test contamination in the shared test database — new catalog tests now
  clean up created skills/paths, restoring order-independent full-suite runs
  (305 backend tests passing).
- Docker healthcheck no longer depends on `curl` (uses Python urllib).

### Removed
- Next.js build coupling in favour of SvelteKit across container configs.
