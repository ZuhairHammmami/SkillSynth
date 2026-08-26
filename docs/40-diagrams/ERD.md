# SkillSynth Database ERD — 15 Tables (Strict 3NF)

```mermaid
erDiagram
    users {
        int id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_admin
        timestamp created_at
        timestamp updated_at
    }

    categories {
        int id PK
        string name UK
        string description
        int parent_id FK
    }

    skills {
        int id PK
        string name UK
        text description
        int difficulty_level
        int estimated_hours
        string icon
        string color
        int category_id FK
    }

    skill_prerequisites {
        int skill_id PK, FK
        int prerequisite_id PK, FK
    }

    job_roles {
        int id PK
        string title UK
        text description
        string career_field
    }

    job_role_skills {
        int job_role_id PK, FK
        int skill_id PK, FK
    }

    resources {
        int id PK
        string title
        string url
        string type
        string language
        boolean is_free
        boolean is_official
        string author_or_platform
        int skill_id FK
    }

    assessments {
        int id PK
        int skill_id FK
        string title
        text description
        int pass_score
        timestamp created_at
        timestamp updated_at
    }

    assessment_questions {
        int id PK
        int assessment_id FK
        int position
        text prompt
        json options
        int correct_index
    }

    assessment_results {
        int id PK
        int user_id FK
        int assessment_id FK
        int score
        boolean passed
        timestamp completed_at
    }

    user_skills {
        int user_id PK, FK
        int skill_id PK, FK
        int proficiency_level
        timestamp last_assessed_at
    }

    paths {
        int id PK
        int user_id FK
        string title
        text description
        string target_role
        string status
        int total_estimated_hours
        int total_estimated_weeks
        timestamp deleted_at
        timestamp created_at
        timestamp updated_at
    }

    path_steps {
        int id PK
        int path_id FK
        int skill_id FK
        int position
        string title
        text description
        int estimated_hours
        json resource_ids
        json assessment_ids
    }

    step_progress {
        int user_id PK, FK
        int step_id PK, FK
        timestamp completed_at
        int score
    }

    activity_log {
        int id PK
        int user_id FK
        string category
        string action
        string entity_type
        string entity_id
        json data
        string ip_address
        string user_agent
        timestamp created_at
    }

    users ||--o{ activity_log : "logs"
    users ||--o{ paths : "owns"
    users ||--o{ assessment_results : "attempts"
    users ||--o{ user_skills : "masters"
    users ||--o{ step_progress : "progresses"
    categories ||--o{ skills : "classifies"
    categories ||--o{ categories : "parent"
    skills ||--o{ skill_prerequisites : "requires"
    skills ||--o{ job_role_skills : "required by"
    skills ||--o{ resources : "linked to"
    skills ||--o{ assessments : "assessed by"
    job_roles ||--o{ job_role_skills : "composed of"
    assessments ||--o{ assessment_questions : "contains"
    assessments ||--o{ assessment_results : "scored by"
    paths ||--o{ path_steps : "contains"
    path_steps ||--o{ step_progress : "tracked by"
```

## Table Inventory (15 total)

| # | Table | Domain | Cascade policy | Notes |
|---|-------|--------|----------------|-------|
| 1 | users | Identity | — | Absorbed profiles; is_admin binary admin flag |
| 2 | categories | Catalog | — | Self-ref parent_id (SET NULL) |
| 3 | skills | Catalog | — | category_id FK (SET NULL); absorbed skill_categories |
| 4 | skill_prerequisites | Catalog (J) | CASCADE | Self-referencing prerequisite DAG |
| 5 | job_roles | Catalog | — | Career role definitions |
| 6 | job_role_skills | Catalog (J) | CASCADE | M:N role→skill |
| 7 | resources | Catalog | SET NULL | skill_id FK optional |
| 8 | assessments | Assessment | SET NULL | skill_id FK; pass_score threshold |
| 9 | assessment_questions | Assessment | CASCADE | Normalized question bank; options JSON (documented exception) |
| 10 | assessment_results | Assessment | CASCADE | Attempt records |
| 11 | user_skills | Assessment | CASCADE | Composite PK (user,skill); real FKs |
| 12 | paths | Learning | CASCADE | Soft delete (deleted_at) |
| 13 | path_steps | Learning | CASCADE | skill_id FK (SET NULL); resource/assessment ids JSON |
| 14 | step_progress | Learning | CASCADE | Merged completions+progress; completed_at = done |
| 15 | activity_log | Engagement | SET NULL | Merged events+audit_logs; category ∈ {audit,auth,system,learning,realtime} |

(J) = Junction table. Cascade policy on FK: CASCADE = ON DELETE CASCADE, SET NULL = ON DELETE SET NULL.

## Notes

- Strict 3NF with 4 documented JSON exceptions: `assessment_questions.options`, `path_steps.resource_ids`, `path_steps.assessment_ids`, `activity_log.data`.
- Canonical DDL: `src/migrations/003_reduced_schema.sql`; verified against ORM by `tools/verify_schema.py` (SCHEMA MATCH — tables, columns, PKs, FKs incl. ON DELETE, uniques, indexes).
- Removal rationale + table→API coverage matrix: `docs/41-decision-records/adr-013.md`.
- Schema unchanged by SS-AI (ADR-015): AI wizard quizzes are ephemeral (SSE-only), practice tests persist in existing `assessments` rows titled `[AI] <Skill> — adaptive`, and proficiency reviews write `user_skills` + `activity_log` only.