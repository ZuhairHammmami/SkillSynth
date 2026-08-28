"""Learning router — knowledge graph, gap analysis and wizard alias.

Wires /api/learning to services/learning_service.py + analytics_service.py
(Task 2). Recommendations is omitted (no service fn in the reduced core);
graph is public like the legacy endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dto.learning import GeneratePathIn, PathDetailOut, RateProficiencyIn
from backend.policies.auth_policy import get_current_user
from backend.repositories import (
    assess_repository as arepo,
    catalog_repository,
    engagement_repository,
)
from backend.repositories import learning_repository as lrepo
from backend.routers.paths import generate_path as _generate_path
from backend.services import analytics_service, learning_service

router = APIRouter()


@router.get("/graph")
def get_knowledge_graph(db: Session = Depends(get_db)):
    """Return the prerequisite knowledge graph (nodes/edges/categories).
    Calls learning_service.build_graph; public like the legacy /learning/graph."""
    return learning_service.build_graph(db)


@router.get("/gaps")
def get_skill_gaps(target_role: str | None = Query(default=None),
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    """Return gap analysis for an optional target job role. Calls
    analytics_service.analyze_gaps; consumed by the student skill-gap UI."""
    return analytics_service.analyze_gaps(db, current_user.id,
                                          target_role=target_role)


@router.get("/analysis")
def learning_analysis(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """GET /learning/analysis — strengths vs weaknesses for the caller.

    Delegates to analytics_service.analyze_weaknesses; consumed by the
    student analytics weaknesses panel (frontend Task 10b).
    """
    return analytics_service.analyze_weaknesses(db, current_user.id)


@router.post("/generate", response_model=PathDetailOut)
def generate_path_alias(data: GeneratePathIn, db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    """Wizard generation alias. Delegates to the canonical /api/generate-path/
    handler (paths.generate_path) so both emit the same learning_service call
    and path_generated SSE event; frontend primary URL is /generate-path/."""
    return _generate_path(data, db, current_user)


@router.put("/skills/{skill_id}/proficiency")
def rate_proficiency(skill_id: int, data: RateProficiencyIn,
                     db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    """Manually rate a skill's proficiency (0..5) for the current user.

    Writes the user_skill row, syncs current_level on that skill's
    PathStep rows and audits a rate.proficiency.set event. Called by the
    student ladder; the frontend re-fetches the path after.
    """
    if not 0 <= data.level <= 5:
        raise HTTPException(status_code=400,
                            detail="level must be between 0 and 5")
    skill = catalog_repository.get_skill(db, skill_id)
    if skill is None:
        raise HTTPException(status_code=400,
                            detail=f"Skill {skill_id} not found")
    arepo.upsert_user_skill(db, current_user.id, skill_id, data.level)
    engagement_repository.write(
        db, "learning", "rate.proficiency.set",
        user_id=current_user.id, entity_type="skill", entity_id=skill_id,
        data={"level": data.level})
    steps = lrepo.update_step_current_level_for_skill(db, skill_id, data.level)
    return {"skill_id": skill_id, "level": data.level,
            "steps": [{"id": s.id, "current_level": s.current_level}
                      for s in steps]}
