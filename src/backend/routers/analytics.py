"""Analytics router — learner dashboards, growth, path progress, history.

Wires /api/analytics to services/analytics_service.py (Task 2). All
endpoints require a signed-in user; consumed by useAnalyticsApi.ts.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.policies.auth_policy import get_current_user
from backend.services import analytics_service

router = APIRouter()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db),
              current_user=Depends(get_current_user)):
    """Return the learner dashboard payload. Calls
    analytics_service.learner_dashboard; consumed by useAnalyticsApi.useAnalyticsDashboard()."""
    return analytics_service.learner_dashboard(db, current_user.id)


@router.get("/skill-growth")
def skill_growth(db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    """Return per-skill growth with mastered/learning/not_started buckets.
    Calls analytics_service.skill_growth; consumed by useAnalyticsApi.useSkillGrowth()."""
    return analytics_service.skill_growth(db, current_user.id)


@router.get("/path-progress/{path_id}")
def path_progress(path_id: int, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    """Return one path's completion progress. Calls
    analytics_service.get_path_progress; None (not owner) maps to 404."""
    result = analytics_service.get_path_progress(db, path_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Path not found")
    return result


@router.get("/learning-history")
def learning_history(db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    """Return recent activity + daily counts. Calls
    analytics_service.learning_history; consumed by useAnalyticsApi.useLearningHistory()."""
    return analytics_service.learning_history(db, current_user.id)
