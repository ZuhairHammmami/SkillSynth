# Functional Requirements

## Core Feature Catalog

### FR-01: Career Selection
| Field | Specification |
|-------|--------------|
| **ID** | FR-01 |
| **Title** | Career Selection |
| **Description** | User selects a career role from categorized, searchable card grid |
| **Flow** | Cards → Searchable Select → Categorized Roles |
| **Constraints** | No free-text input. Role data from `job_roles` table (25 seeded roles) |
| **UI Pattern** | Card grid with role title, description, career_field badge. Search filters by title/career_field |
| **Acceptance** | User must select exactly 1 role before proceeding. "Next" disabled until selection made |

### FR-02: Preferences Collection
| Field | Specification |
|-------|--------------|
| **ID** | FR-02 |
| **Title** | Learning Preferences |
| **Description** | User selects skill level, weekly hours, content format, language, free-only toggle |
| **Inputs** | Skill level (beginner/intermediate/advanced), Weekly hours (1-40 slider), Format (any/video/article/course), Language (en/ar), Free content only (boolean) |
| **Default** | intermediate, 10h, any, en, free=true |
| **Acceptance** | All fields have defaults. User can proceed without changing anything |

### FR-03: Skills Assessment
| Field | Specification |
|-------|--------------|
| **ID** | FR-03 |
| **Title** | Skills Assessment |
| **Description** | Adaptive assessment covering skills relevant to selected career role |
| **Scoring** | Score % → level mapping: 100%=5, ≥80%=4, ≥60%=3, ≥40%=2, >0%=1, 0%=0 |
| **Format** | Multiple choice, 5 questions per skill, randomized options |
| **Acceptance** | Assessment for each skill in the role. Results stored in `assessment_results` table |

### FR-04: Path Generation
| Field | Specification |
|-------|--------------|
| **ID** | FR-04 |
| **Title** | Path Generation |
| **Description** | Deterministic topological-sorted path based on assessment + prerequisite graph |
| **Algorithm** | Kahn's topological sort on DAG. Fallback prerequisites map for DB gaps |
| **Output** | Ordered steps with resources (main + additional), estimated hours, difficulty labels |
| **Acceptance** | Same inputs → same outputs (deterministic). No LLM involved |

### FR-05: Progress Tracking
| Field | Specification |
|-------|--------------|
| **ID** | FR-05 |
| **Title** | Progress Tracking |
| **Description** | Step-by-step completion with undo, real-time SSE updates |
| **Events** | `progress_update`, `xp_update` (naming kept for API compat, no XP displayed) |
| **Acceptance** | Completing step persists to `step_completions`, invalidates React Query cache |

### FR-06: Admin Management
| Field | Specification |
|-------|--------------|
| **ID** | FR-06 |
| **Title** | Admin Management |
| **Description** | 11 admin pages: dashboard, users, skills, categories, paths, resources, job-roles, settings, audit-log, analytics, reports |
| **Access** | `is_admin=True` required. All admin routes guarded by `get_current_admin_user` |
| **Audit** | All mutations logged to `audit_logs` table. SSE stream available in audit-log page |

### FR-07: Real-time Updates
| Field | Specification |
|-------|--------------|
| **ID** | FR-07 |
| **Title** | Real-time Progress |
| **Description** | SSE + WebSocket for real-time progress, notifications, admin alerts |
| **Events** | 14 event types: progress_update, path_completion, assessment_result, notification, admin_alert, etc. |
| **Acceptance** | SSE auto-reconnects. React Query cache invalidation on event receipt |

## Traceability Matrix
| FR ID | Backend Endpoint | Frontend Route | Test File |
|-------|-----------------|----------------|-----------|
| FR-01 | `GET /api/wizard-options` | `/wizard` (GoalStep) | `test_paths.py` |
| FR-02 | `GET /api/wizard-options` | `/wizard` (PreferencesStep) | `test_skills.py` |
| FR-03 | `GET /api/assessments/{role}` | `/wizard` (AssessmentStep) | `test_assessments.py` |
| FR-04 | `POST /api/generate-path/` | `/wizard` (SummaryStep → /paths) | `test_paths.py` |
| FR-05 | `POST /api/steps/{id}/complete` | `/learn/[id]` | `test_paths.py` |
| FR-06 | `GET /api/admin/*` | `/admin/*` | `test_admin.py` |
| FR-07 | `GET /api/realtime/events` | All pages (useSSE hook) | Manual |
