# SS-EDS: Learning Engine

## Purpose
Document the deterministic learning engine with 3 core services (LearningEngine, LearningAnalyzer, ResourceRecommender), prerequisite DAG topological sort, personalized path generation, and 7 REST API endpoints.

## Responsibilities
- Topological sort of skill prerequisite graph (Kahn's algorithm)
- Generate personalized learning paths with gap analysis
- Identify skill gaps and recommend focus areas
- Estimate time to mastery per skill/role
- Select and filter learning resources by preferences
- Build knowledge graph data for visualization
- Provide 7 learning API endpoints

## Inputs
- User skill profile (current levels per skill)
- Goal skills or job role targets
- Weekly hours commitment and preferences
- Resource catalog with type, language, pricing metadata
- Skill prerequisite graph from DB

## Outputs
- Personalized path with ordered steps, resources, time estimates
- Skill gap analysis (weaknesses, strengths, recommended focus)
- Time estimates per skill with weekly breakdown
- Resource recommendations filtered by preferences
- Knowledge graph data (nodes + edges for frontend visualization)

## Dependencies
- 10-database (skills, skill_prerequisites, resources, categories tables)
- backend.repositories.learning_repository (the current learning data-access module; the queries/ layer was removed per ADR-013)
- 12-realtime (SSE events on path generation)

## Sequence: Personalized Path Generation
```
User Input (goal_skills, skill_profile, weekly_hours, preferences)
  ↓
LearningEngine.generate_personalized_path()
  → LearningAnalyzer.identify_skill_gaps()
    → LearningEngine.get_prerequisite_chain() (DFS)
  → For each gap: check status, build prerequisite steps
  → ResourceRecommender.pick_resource() for each step
  → Calculate total hours and weeks
  ↓
Return {steps, total_hours, total_weeks, description}
```

## State Diagram: Skill Proficiency
```
[Not Started (0)] → [Learning (1-2)] → [Competent (3-4)] → [Mastered (5)]
       ↓                   ↓                    ↓
[Gap Analysis]     [Prerequisite Check]   [Skipped in path gen]
```

## API Endpoints
| Endpoint | Method | Service | Description |
|----------|--------|---------|-------------|
| /api/learning/graph | GET | ResourceRecommender | Full knowledge graph (nodes, edges, categories) |
| /api/learning/path/generate | GET | LearningEngine | Generate personalized path for goal skills |
| /api/learning/analysis | GET | LearningAnalyzer | Weakness/strength analysis for profile |
| /api/learning/recommendations | POST | ResourceRecommender | Filtered resource recommendations |
| /api/learning/progress | GET | LearningAnalyzer | Progress by category |
| /api/learning/time-estimate | GET | LearningAnalyzer | Time estimate for goal skills |
| /api/learning/skill-gaps | GET | LearningAnalyzer | Identify gaps between current and target |

## Rules
1. Skill levels: 0=not_started, 1-2=learning, 3-4=competent, 5=mastered
2. Skills at level ≥ 3 are mastered — skipped during path generation
3. Prerequisites form a DAG — sorted via Kahn's algorithm
4. Resources filtered by: is_free=true, preferred language, preferred format
5. No exceptions thrown — all services return fallback/empty on failure

## Examples
- User with html=4, css=3, js=2 → path starts with JavaScript advanced topics
- Frontend role → html → css → javascript → react → typescript chain
- Gap analysis returns weaknesses sorted by gap size (largest first)

## Edge Cases
- Empty skill profile → no skills mastered, full path generated
- Prerequisite cycle → Kahn's algorithm detects and skips cyclic edges
- All skills mastered → empty path, user notified
- No resources match filters → content-only steps with no external links

## Failure Cases
- DB connection fails → fallback to empty results, logged error
- Goal skill not found in DB → marked as "unknown" with level 0
- Resource picker finds no candidates → returns None, step has no resource

## Recovery Procedures
1. Check DB connectivity and seed data integrity
2. Verify skill_prerequisites table has valid DAG (no cycles)
3. Run `PYTHONPATH=src python seed_v3.py` to reset learning data

## Refactoring Strategy
- Extract personalized path generation into Strategy pattern
- Add A/B testing for different path generation algorithms
- Cache knowledge graph data with Redis for faster visualization
