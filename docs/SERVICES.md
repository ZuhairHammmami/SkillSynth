# Services — DEPRECATED (absorbed into SS-EDS sections)

> **⚠️ Gamification functions:** `award_xp`, `deduct_xp`, `check_and_award_completion_achievements`, `get_user_gamification_data` — all **REMOVED**.

## Service Inventory

| Service | File | Pattern | Integration Status |
|---------|------|---------|-------------------|
| **HybridLLMProvider** | `src/services/HybridLLMProvider.ts` (609 lines) | Static class | Functional |
| **VectorSearchService** | `src/services/VectorSearchService.ts` (463 lines) | Instance class w/ DI | Functional (standalone) |
| **ProjectSubmissionService** | `src/services/ProjectSubmissionService.ts` (327 lines) | Static class | Stubbed (no DB ops) |
| **NotificationService** | `src/services/shared/notification/NotificationService.ts` (151 lines) | Static class | Not wired (imports commented out) |
| **ConflictCheckerService** | `src/services/shared/conflict-checker/ConflictCheckerService.ts` (148 lines) | Pure static | Re-implemented as frontend stub |
| **Email Service** | `src/backend/email_service.py` (61 lines) | Standalone functions | Functional (password reset) |
| **Gamification** | `src/backend/gamification.py` (153 lines) | Standalone functions | Functional (full integration) |

## HybridLLMProvider

**Strategy**: Local-first → OpenAI fallback → Static fallback (never throws).

```mermaid
generateExplanation() / generateQuiz()
  ├── If provider=local|hybrid AND Ollama healthy
  │   ├── Success → return result
  │   └── Fail (and hybrid+fallbackToOpenAI) → try OpenAI
  │       ├── Success → return result
  │       └── Fail → return static fallback
  ├── If provider=openai → OpenAI directly
  │   ├── Success → return result
  │   └── Fail → static fallback
  └── Static fallback (hardcoded templates)
```

| Provider | Model | Endpoint | Timeout |
|----------|-------|----------|---------|
| Local (Ollama) | `mistral` (configurable) | `http://localhost:11434/api/generate` | 10s gen, 2s health |
| OpenAI | `gpt-4` (configurable) | `https://api.openai.com/v1/chat/completions` | 15s |

**Health cache**: 5min TTL, 3-consecutive-failure threshold.

**Env vars**: `LLM_PROVIDER`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OPENAI_API_KEY`, `OPENAI_MODEL`

## VectorSearchService

- Generates embeddings via local (`http://localhost:8000/embed`, `all-MiniLM-L6-v2`) or OpenAI (`text-embedding-3-small`)
- Searches via pgvector cosine distance (`<=>`)
- Supports batch embedding with cost tracking
- Uses `DatabaseLike` interface for DI

## Gamification (Python Backend)

| Function | Effect |
|----------|--------|
| `award_xp(db, profile_id, amount, reason)` | +XP, level calc (each level = `level * 100` XP), awards `level_N` achievement |
| `deduct_xp(db, profile_id, amount, reason)` | -XP (floor 0), recalculates level down |
| `update_streak(db, profile_id)` | Daily streak: extends, resets on gap, milestones at 3/7/14/21/30/60/100 |
| `check_and_award_completion_achievements(db, profile_id)` | Milestones: 1/10/50/100 steps |
| `get_user_gamification_data(db, profile_id)` | Aggregated snapshot |

**XP Economy**: +10 per step complete, -10 per undo.

## NotificationService (SendGrid)

- Sends transactional emails via SendGrid v3 API (Axios)
- Methods: `sendEmail`, `notifyKnowledgeIngestion`, `notifyPrerequisiteConflict`, `sendSystemAlert`
- Wired to: **Nothing** — all imports in API routes are commented out

## ConflictCheckerService

- Pure functions (no I/O): `checkNodeTransition`, `validateSkillOverrides`, `getBlockedNodes`
- Validates prerequisite chains for `UserPath` transitions
- Consumed by frontend stub `ConflictNotificationService` with sonner toasts
- `useConflictDetection` hook + `useConflictPreview` hook (inline circular reference detection)

## Pattern: All TypeScript Services

All follow the same pattern: never throw, always return fallback/empty result + `console.log` instead of structured logging. Static class methods are the dominant pattern.
