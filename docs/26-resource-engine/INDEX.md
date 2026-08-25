# SS-EDS: Resource Engine

## Purpose
Document the resource selection and management system for SkillSynth. Covers resource metadata, filtering, selection strategy, and deduplication for learning path resources.

## Responsibilities
- Maintain resource catalog (87+ resources in seed_all.py)
- Implement resource selection algorithm (language, format, free/premium, official priority)
- Handle resource deduplication by URL
- Support multiple resource types (video, article, book, course, documentation)

## Inputs
- Resource metadata from seed_all.py / src/data/learning_paths/resources.json
- Learner preferences (language, format)
- Skill-to-resource mappings

## Outputs
- Selected resource lists for each path step
- Deduplicated resource assignments

## Dependencies
- 10-database (resources table)
- 11-learning-engine (path generation uses resource selection)
- 05-domain (resource-to-skill relationships)

## Sequence: Resource Selection
```
Path Generator → select_resources(skills, prefs)
  → Query resources for each skill
  → Filter by language (Arabic preferred if available)
  → Filter by format preference
  → Prioritize free resources over paid
  → Prioritize official resources (documentation, courses)
  → Deduplicate by URL
  → Return unique resource list
  → Assign to path steps
```

## State Diagram: Resource Lifecycle
```
[Draft] → [Published] → [Deprecated] → [Archived]
             ↓
       [Updated]
```

## ERD References
- resources table: title, url, type, is_free, is_official, author_or_platform, language
- path_steps: resource_ids (JSON array referencing resources)

## Resource Types
| Type | Description | Priority |
|------|-------------|----------|
| documentation | Official docs, reference | Highest |
| course | Structured online course | High |
| video | Tutorial video | Medium |
| article | Blog post, guide | Medium |
| book | Textbook, ebook | Low |
| interactive | Coding platform, sandbox | Medium |

## Rules
1. Resources deduplicated by URL before assignment
2. Free resources preferred over paid
3. Official documentation prioritized over third-party
4. Language preference filters before other criteria
5. Maximum 3-5 resources per skill per step
6. Resources must be unique within a path

## Examples
- Learner with language="ar": Arabic resources selected first, English fallback
- Learner with format="video": video resources prioritized

## Edge Cases
- No matching resources for a skill after filtering → step content-only (no external links)
- Same resource URL appears for multiple skills → deduplicated, assigned to first matching skill
- Resource URL broken/unavailable → logged but not removed from DB

## Failure Cases
- resources table empty → fallback to resources.json
- Resource type not recognized → defaults to "article"
- All resources filtered out → empty resource section in step

## Recovery Procedures
1. Seed resources with `python seed_all.py`
2. Verify resource URLs are accessible
3. Check resource filter criteria against database

## Refactoring Strategy
- Migrate from JSON file to fully DB-backed resources
- Add resource quality scoring (ratings, relevance score)
- Implement resource version tracking for updates
- Add resource caching for frequently accessed items
