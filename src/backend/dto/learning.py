"""Learning DTOs — wizard options, path generation, progress, graph.

Consumed by services/learning_service.py and the learning/progress routers
(Task 3). Wire keys are frozen: PathOut.id is an int, steps keep
`content` + `is_completed`, dashboard keeps total_paths/completed_steps/etc.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WizardRoleInfo(BaseModel):
    """One job-role entry inside WizardOptionsOut payloads."""

    title: str
    description: Optional[str] = None
    career_field: str = "Other"


class WizardPreferencesOptions(BaseModel):
    """Literal format/language choices offered by the wizard."""

    formats: List[str]
    languages: List[str]


class WizardOptionsOut(BaseModel):
    """GET /wizard-options response (shape frozen; consumed by frontend)."""

    job_roles: List[WizardRoleInfo]
    career_fields: dict[str, list[WizardRoleInfo]]
    preferences: WizardPreferencesOptions


class DetailedPreferences(BaseModel):
    """Resource preference filters inside GeneratePathIn."""

    is_free: Optional[bool] = True
    format: Optional[str] = "any"
    language: Optional[str] = "en"


class GeneratePathIn(BaseModel):
    """POST /generate-path body; answers keyed "<skill>_q<i>" -> index."""

    goal: str = Field(..., json_schema_extra={"example": "Frontend Developer"})
    weekly_hours: int = Field(..., json_schema_extra={"example": 10})
    preferences: DetailedPreferences
    answers: dict[str, int] = Field(default_factory=dict)


class StepResource(BaseModel):
    """Resource card embedded inside StepOut.resources."""

    id: int
    title: str
    url: str
    type: str


class StepOut(BaseModel):
    """Serialized path_steps row; `content` mirrors entity.description
    and `is_completed` is synthesized from step_progress.completed_at."""

    id: int
    step_number: int
    title: str
    content: Optional[str] = None
    is_completed: bool = False
    resources: list[StepResource] = []
    resource_ids: Optional[list[int]] = None
    assessment_ids: Optional[list[int]] = None


class PathOut(BaseModel):
    """Serialized paths row; id is an int (frontend TS contract)."""

    id: int
    profile_id: int
    title: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    total_estimated_hours: Optional[int] = None
    total_hours: Optional[int] = None
    total_estimated_weeks: Optional[int] = None
    goal_job_role: Optional[str] = None
    created_at: Optional[datetime] = None
    steps: list[StepOut] = []
    skills: list[dict] = []


class PathDetailOut(PathOut):
    """Alias of PathOut with full per-step resources; distinct name so
    routers (Task 3) can annotate detail endpoints explicitly."""


class ProgressPathOut(BaseModel):
    """Per-path block inside ProgressDashboardOut.paths."""

    id: int
    title: str
    description: Optional[str] = None
    total_estimated_hours: Optional[int] = None
    total_hours: Optional[int] = None
    total_estimated_weeks: Optional[int] = None
    goal_job_role: Optional[str] = None
    created_at: Optional[str] = None
    steps: list[StepOut] = []


class ProgressDashboardOut(BaseModel):
    """GET /progress/dashboard response — key contract owned by the
    live frontend (progress page): total_paths, total_steps,
    completed_steps, completion_percentage, remaining_hours,
    total_hours. `weekly` and `paths` are additive extras."""

    total_paths: int
    total_steps: int
    completed_steps: int
    completion_percentage: float
    remaining_hours: float
    total_hours: float
    weekly: int = 0
    paths: list[ProgressPathOut] = []


class StepCompletionResponse(BaseModel):
    """POST /progress/steps/{id}/complete response; key profile_id is
    kept (not user_id) for wire compatibility with the frontend."""

    profile_id: int
    step_id: int
    completed_at: datetime


class GraphNode(BaseModel):
    """Skill node in the knowledge graph payload."""

    id: int
    name: str
    difficulty: int
    icon: Optional[str] = None
    color: Optional[str] = None
    category_ids: list[int] = []
    resource_count: int = 0


class GraphEdge(BaseModel):
    """Prerequisite edge; source must be learned before target."""

    source: int
    target: int
    type: str = "prerequisite"


class GraphCategory(BaseModel):
    """Category entry in the knowledge graph payload."""

    id: int
    name: str


class GraphOut(BaseModel):
    """GET /learning/graph response (nodes/edges/categories)."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
    categories: list[GraphCategory]


class GapPrerequisite(BaseModel):
    """Unmet prerequisite attached to a gap entry."""

    id: int
    name: str
    current_level: int
    needed: int


class GapItem(BaseModel):
    """One skill gap in GapsOut.gaps; unknown skills degrade gracefully."""

    skill: str
    skill_id: Optional[int] = None
    status: str
    current_level: int = 0
    target_level: Optional[int] = None
    gap: Optional[int] = None
    difficulty: Optional[int] = None
    prerequisites: list[GapPrerequisite] = []


class GapsOut(BaseModel):
    """GET /learning/skill-gaps response."""

    goal_skills: list[str]
    gaps: list[GapItem]


class PathUpdate(BaseModel):
    """PUT /paths/{id} body; only provided fields are applied."""

    title: Optional[str] = None
    description: Optional[str] = None


class WizardAnalysisIn(BaseModel):
    """POST /wizard/analysis body — same answer-key contract as
    GeneratePathIn.answers; weekly_hours feeds the weeks estimate."""

    goal: str
    weekly_hours: int = 10
    answers: dict[str, int] = Field(default_factory=dict)
