"""Learning router — knowledge graph, gap analysis and wizard alias.

Wires /api/learning to services/learning_service.py + analytics_service.py
(Task 2). Recommendations is omitted (no service fn in the reduced core);
graph is public like the legacy endpoint.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dto.learning import GeneratePathIn, PathDetailOut
from backend.policies.auth_policy import get_current_user
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
