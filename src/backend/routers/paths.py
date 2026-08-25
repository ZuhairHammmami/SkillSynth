"""Paths router — wizard generation, path CRUD, step progress, dashboard.

Wires /api/generate-path, /api/paths, /api/steps, /api/progress/dashboard,
/api/wizard-options and /api/wizard/analysis to services/learning_service.py
+ wizard_service.py (Task 2) + llm_pipeline (SS-AI Task 7). Consumed by
usePathApi.ts and useSystemApi.ts.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config import app_settings as settings
from backend.database import get_db
from backend.dto.learning import (
    GeneratePathIn, PathDetailOut, PathUpdate,
    StepCompletionResponse, WizardAnalysisIn, WizardOptionsOut,
)
from backend.events.publisher import send_event
from backend.policies.auth_policy import get_current_user
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.repositories import learning_repository as lrepo
from backend.services import llm_pipeline, learning_service, wizard_service
from backend.services.analytics_service import MASTERY_LEVEL
from backend.services.assess_service import normalize_key

router = APIRouter()


@router.post("/generate-path/", response_model=PathDetailOut)
def generate_path(data: GeneratePathIn, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    """Generate a learning path from wizard input. Calls
    learning_service.generate_path; consumed by usePathApi.useGeneratePath()."""
    result, error = learning_service.generate_path(db, current_user, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    send_event(current_user.id, "path_generated", {"path_id": result["id"]})
    return result


@router.get("/paths/")
def list_paths(db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    """List the user's paths as full detail payloads. Calls
    learning_service.list_user_paths; consumed by usePathApi.usePaths()."""
    return learning_service.list_user_paths(db, current_user.id)


@router.get("/paths/{path_id}", response_model=PathDetailOut)
def get_path(path_id: int, db: Session = Depends(get_db),
             current_user=Depends(get_current_user)):
    """Fetch one owned path with steps[].is_completed. Calls
    learning_service.format_path_detail; consumed by usePathApi.usePathDetail()."""
    path = lrepo.get_path(db, path_id, current_user.id)
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    return learning_service.format_path_detail(db, path, current_user.id)


@router.put("/paths/{path_id}", response_model=PathDetailOut)
def update_path(path_id: int, data: PathUpdate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Apply PathUpdate fields to an owned path. Calls the learning
    repository update; consumed by usePathApi.useUpdatePath()."""
    path = lrepo.get_path(db, path_id, current_user.id)
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    updated = lrepo.update_path(db, path, data.model_dump(exclude_unset=True))
    return learning_service.format_path_detail(db, updated, current_user.id)


@router.delete("/paths/{path_id}")
def delete_path(path_id: int, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Hard-delete an owned path. Calls the learning repository delete;
    consumed by usePathApi.useDeletePath()."""
    if not lrepo.delete_path(db, path_id, current_user.id):
        raise HTTPException(status_code=404, detail="Path not found")
    return {"detail": "Path deleted"}


@router.post("/steps/{step_id}/complete", response_model=StepCompletionResponse)
def complete_step(step_id: int, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    """Mark a step complete (idempotent). Calls learning_service.complete_step;
    consumed by usePathApi.useCompleteStep()."""
    result, error, status = learning_service.complete_step(
        db, current_user.id, step_id)
    if error:
        raise HTTPException(status_code=status, detail=error)
    return result


@router.post("/steps/{step_id}/undo-complete")
def undo_complete_step(step_id: int, db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    """Revert a step completion. Calls learning_service.undo_complete_step;
    consumed by usePathApi.useUndoCompleteStep()."""
    result, error, status = learning_service.undo_complete_step(
        db, current_user.id, step_id)
    if error:
        raise HTTPException(status_code=status, detail=error)
    return result


@router.get("/progress/dashboard")
def progress_dashboard(db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    """Return the progress dashboard payload. Calls
    learning_service.progress_dashboard; consumed by usePathApi.useDashboard()."""
    return learning_service.progress_dashboard(db, current_user.id)


@router.get("/wizard-options", response_model=WizardOptionsOut)
def wizard_options(db: Session = Depends(get_db)):
    """Return wizard source data (job roles, career fields, preferences).
    Calls services/wizard_service.wizard_options; consumed by useSystemApi.useWizardOptions()."""
    return wizard_service.wizard_options(db)


@router.post("/wizard/analysis")
def wizard_analysis(data: WizardAnalysisIn, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    """Phase-1 detailed results BEFORE path creation (SS-AI spec).

    Calls learning_service._score_answers(persist=False) purely, then
    _build_report_rows for rows/lists; optionally enriches with
    llm_pipeline.analyze_diagnostic when settings.AI_ENABLED. Performs
    ZERO writes. Consumed by PathWizard ResultsStep (frontend Task 10).
    """
    role = catalog_repository.get_job_role_by_title(db, data.goal)
    if not role:
        raise HTTPException(status_code=404, detail="Unknown job role")
    skills = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    if not skills:
        raise HTTPException(status_code=404, detail="Role has no skills")
    levels = learning_service._score_answers(
        db, skills, data.answers or {}, current_user.id, persist=False)
    previous = arepo.get_skill_profile(db, current_user.id)
    per_skill, weaknesses, strengths = _build_report_rows(
        db, skills, data.answers or {}, levels, previous)
    hours = sum((s.estimated_hours or 10) for s in skills
                if levels[s.id] < MASTERY_LEVEL)
    report = {
        "per_skill": per_skill, "weaknesses": weaknesses,
        "strengths": strengths,
        "recommended_focus": weaknesses[:5],
        "estimated_weeks": max(1, round(hours / max(data.weekly_hours, 1))),
        "narrative": None, "narrative_available": False,
    }
    if settings.AI_ENABLED and llm_pipeline._engine_available():
        narrative = llm_pipeline.analyze_diagnostic(per_skill)
        if narrative:
            report.update(narrative=narrative, narrative_available=True)
    return report


def _build_report_rows(db, skills, answers, levels, previous):
    """Assemble per_skill rows + weakness/strength lists (pure).

    Helper keeping wizard_analysis under the 40-line cap; tallies grade
    answers against the skill's FIRST assessment's ordered questions,
    mirroring learning_service._score_answers semantics without writes.
    """
    assessments = arepo.get_assessments_for_skills(
        db, [s.id for s in skills])
    rows, weak, strong = [], [], []
    for s in skills:
        questions = (arepo.get_questions(db, assessments[s.id].id)
                     if s.id in assessments else [])
        keyed = [(i, answers[k])
                 for i, _ in enumerate(questions)
                 for k in [f"{normalize_key(s.name).lower()}_q{i}"]
                 if k in answers]
        correct = sum(1 for i, v in keyed
                      if v == questions[i].correct_index)
        total, ans_n = len(questions), len(keyed)
        lvl = levels[s.id]
        prev = previous.get(s.name, 0)
        rows.append({"skill": s.name, "skill_id": s.id,
                     "correct": correct if total else 0, "total": total,
                     "answered_count": ans_n, "assessed_level": lvl,
                     "previous_level": prev,
                     "gap_to_mastery": max(0, MASTERY_LEVEL - lvl),
                     "weakness": lvl < 2})
        if total and lvl < 2:
            weak.append(s.name)
        if lvl >= MASTERY_LEVEL:
            strong.append(s.name)
    return rows, weak, strong
