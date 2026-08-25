# Data Layer — DEPRECATED (absorbed into SS-EDS docs/10-database/)

## Dual Data Sources

SkillSynth has two parallel data systems that overlap:

```
STATIC JSON FILES (legacy/standalone)       DATABASE (primary via seed_all.py)
─────────────────────────────               ──────────────────────────────────
rules.json (7 job roles)      ──→           skills (79), job_roles (19)
resources.json (50+ skills)   ──→           resources (89)
assessments.json (50 skills)  ──→           assessments (one per skill)
                                            categories (16)
                                            profiles (2: admin + demo)
                                            paths + path_steps (3 demo)
```

## Seed Scripts

| Script | Tables | Run when |
|--------|--------|----------|
| **`python seed_all.py`** | All 10+ tables (authoritative) | First setup, DB reset |
| `python src/scripts/seed.py` | Minimal: 2 categories, 6 skills, 1 job role | PostgreSQL-only testing |
| `npx ts-node src/scripts/seed-engineering-path.ts` | Engineering path DAG | Phase 3 testing |

`seed_all.py` is idempotent — checks `existing_skills_count > 0` before seeding.

## Learning Path Generation Pipeline

```
Wizard Input (goal, answers, hours, prefs)
  │
  ▼
run_assessment(goal, user_answers)         [assessor.py]
  │ Reads assessments.json
  │ Scores per skill → skill_levels (0-5)
  ▼
generate_path(profile, goal, hours, prefs) [generator.py]
  │ 1. fetch_skills_for_job_role()          [db_connector.py]
  │ 2. fetch_role_skill_config()            [db_connector.py]
  │ 3. Build prerequisite DAG (DB + PREREQ_FALLBACK hardcoded dict)
  │ 4. Skip mastered skills (level ≥ 3)
  │ 5. Topological sort (Kahn's algorithm)
  │ 6. Group into steps with resources
  │ 7. select_resources() — filters by lang, format, free, official priority
  ▼
Stored as Path + PathStep in DB → returned to frontend
```

## Static JSON Files

| File | Location | Content |
|------|----------|---------|
| `rules.json` | `src/data/learning_paths/rules.json` | 7 job roles → skill list with hours |
| `resources.json` | `src/data/learning_paths/resources.json` | 6780 lines, ~50 skills → resource links |
| `assessments.json` | `src/data/learning_paths/assessments.json` | 5057 lines, ~50 skills → 5 questions each |

## DB Connector (`db_connector.py`)

Standalone SQLAlchemy engine (separate from main `database.py`). Reads `.env` independently.
Uses `LIKE` for SQLite, `ILIKE` for PostgreSQL.

| Function | Query |
|----------|-------|
| `fetch_skills_for_job_role(title)` | Skills by job role title |
| `fetch_resources_for_skill(skill_id)` | Resources tagged to skill |
| `fetch_prerequisites_for_skills(ids)` | Prerequisite graph |
| `fetch_role_skill_config(title)` | Ordering + hours from config table |
| `fetch_all_skill_names()` | All skills for normalization |

## AEIS Schema (Supabase Migrations)

**Location**: `src/migrations/` — 5 SQL files targeting Supabase PostgreSQL.

| Migration | Tables | Purpose |
|-----------|--------|---------|
| `001_aeis_initial_schema.sql` | concepts, concept_prerequisites, engineering_projects, project_concepts, users, user_mastery | Core AEIS knowledge graph |
| `002_phase_3_4_adaptive_learning.sql` | assessment_results, user_stuck_tracking, alternative_explanations, skill_gaps, learning_interventions | Adaptive learning |
| `003_phase_4_0_ecosystem_synchrony.sql` | project_node_requirements, project_submissions, github_validation_cache, community_templates, shared_learning_paths, path_clones, llm_usage_analytics | Ecosystem |
| `004_phase_4_5_vector_search.sql` | concept_embeddings (pgvector), embedding_metadata, vector_search_queries | Vector search |
| `005_create_user_path.sql` | user_path | User ~~mastery~~ paths |

**Key**: AEIS uses UUID PKs, RLS policies, confidence scoring (>0.7 enforced).
The main learning path system (SQLAlchemy) uses integer IDs and is **separate** from AEIS.

## Skill Profile Data

Stored as JSON on `profiles.skill_profile`:
```json
{
  "html": 4,
  "css": 3,
  "javascript": 2,
  "python": 0
}
```
Levels: 0=not_started, 1-2=learning, 3-4=competent, 5=mastered
Skills with level ≥ 3 are "mastered" and skipped during path generation.

## Name Normalization

All skill names are normalized for matching:
```python
lower() → replace(' ', '_') → replace('.', '_') → replace('-', '_')
       → strip '()' → replace('&', 'and') → strip "'"
```
