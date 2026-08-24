"""Entity package — the 15-table reduced schema (Task 1, 003 migration).

Re-exports Base plus every entity class so that
`Base.metadata.create_all` builds exactly the 15 canonical tables and
`import backend.entities` registers them all.
"""

from backend.entities.base import Base
from backend.entities.identity import User
from backend.entities.catalog import (
    Category,
    JobRole,
    JobRoleSkill,
    Resource,
    Skill,
    SkillPrerequisite,
)
from backend.entities.assessment import (
    Assessment,
    AssessmentQuestion,
    AssessmentResult,
)
from backend.entities.learning import (
    Path,
    PathStep,
    StepProgress,
    UserSkill,
)
from backend.entities.engagement import ActivityLog

__all__ = [
    "Base",
    "User",
    "Category",
    "Skill",
    "SkillPrerequisite",
    "JobRole",
    "JobRoleSkill",
    "Resource",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentResult",
    "UserSkill",
    "Path",
    "PathStep",
    "StepProgress",
    "ActivityLog",
]
