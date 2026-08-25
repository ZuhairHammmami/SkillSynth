# Domain Model

## Core Entities

### Career Domain
```
JobRole ──< JobRoleSkill >── Skill
  │                             │
  │                   SkillCategory >── Category
  │                             │
  │               SkillPrerequisite (self-ref DAG)
  │
  └─── Assessment >── AssessmentResult (per user)
```

### Learning Path Domain
```
Path ──< PathSkill >── Skill
  │
  └── PathStep ──< StepCompletion (per user)
       │
       └── Resource (via resource_ids JSON)
```

### Auth Domain
```
User ──< UserRole >── Role ──< RolePermission >── Permission
  │
  └── Profile (1:1, CASCADE)
  │
  └── Session
```

### Analytics Domain
```
Event
Notification
AnalyticsEvent
Streak
AuditLog
```

## Ubiquitous Language
| Term | Definition |
|------|------------|
| Path | Ordered collection of steps toward a career goal |
| Step | Single unit of learning (skill acquisition) |
| Skill | A defined technical competency |
| Prerequisite | Required skill before another can be learned |
| Assessment | Test measuring current skill level |
| Gap | Difference between current and required skill level |
| Profile | User identity + preferences + progress summary |
| DAG | Directed Acyclic Graph of skill prerequisites |
