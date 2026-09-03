"""Paths router — wizard generation, path CRUD, step progress, dashboard.

Wires /api/generate-path, /api/paths, /api/steps, /api/progress/dashboard,
/api/wizard-options and /api/wizard/analysis to services/learning_service.py
+ wizard_service.py (Task 2) + llm_pipeline (SS-AI Task 7). Consumed by
usePathApi.ts and useSystemApi.ts.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import app_settings as settings
from backend.database import get_db
from backend.dto.learning import (
    GeneratePathIn, PathDetailOut, PathUpdate,
    StepCompletionResponse, WizardAnalysisIn, WizardOptionsOut,
)
from backend.dto.pagination import paginate
from backend.events.publisher import send_admin_event, send_event
from backend.policies.auth_policy import get_current_user
from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.repositories import learning_repository as lrepo
from backend.services import llm_pipeline, learning_service, wizard_service
from backend.services import settings_service
from backend.services import step_test_service
from backend.services.analytics_service import MASTERY_LEVEL
from backend.services.assess_service import normalize_key

router = APIRouter()


@router.post("/generate-path/", response_model=PathDetailOut)
def generate_path(data: GeneratePathIn, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    """Generate a learning path from wizard input. Calls
    learning_service.generate_path; consumed by usePathApi.useGeneratePath().
    Broadcasts to both the owner's channel and the admin SSE channel so the
    admin /paths table can refresh."""
    result, error = learning_service.generate_path(db, current_user, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    send_event(current_user.id, "path_generated", {"path_id": result["id"]})
    send_admin_event("path_generated", {
        "path_id": result["id"], "title": result.get("title")})
    return result


class GenerateSkillPathIn(BaseModel):
    """POST /generate-path/skill/{id} body — weekly time budget + prefs."""

    weekly_hours: int = 10
    preferences: dict | None = None


@router.post("/generate-path/skill/{skill_id}", response_model=PathDetailOut)
def generate_path_for_skill(skill_id: int, data: GenerateSkillPathIn,
                            db: Session = Depends(get_db),
                            current_user=Depends(get_current_user)):
    """Generate a learning path from a single catalog skill (endpoint C).

    Calls learning_service.generate_path_for_skill, reusing the wizard
    prereq-ordering/persistence helpers additively (no change to the
    existing wizard flow). Raises 404 (unknown skill) or 409 (already in a
    path / all mastered). Broadcasts path events for dashboard refresh."""
    result, error = learning_service.generate_path_for_skill(
        db, current_user, skill_id,
        weekly_hours=data.weekly_hours, preferences=data.preferences)
    if error:
        status = 409 if "already" in error or "mastered" in error else 404
        raise HTTPException(status_code=status, detail=error)
    send_event(current_user.id, "path_generated", {"path_id": result["id"]})
    send_admin_event("path_generated", {
        "path_id": result["id"], "title": result.get("title")})
    return result


@router.get("/paths/")
def list_paths(page: int = 1, page_size: int = 50,
               db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    """List the user's paths paginated. Calls
    learning_service.list_user_paths; consumed by usePathApi.usePaths()."""
    return paginate(learning_service.list_user_paths(db, current_user.id),
                    page, page_size)


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


class StepTestSubmitIn(BaseModel):
    """POST /steps/{step_id}/test/submit body — answers keyed by question id."""

    assessment_id: int
    answers: dict[str, int] = {}


def _locale_from_request(request: Request) -> str:
    """Resolve request locale: LOCALE cookie, then Accept-Language, else en.

    Callee of the step-test endpoints so generated quizzes match the UI
    language the learner selected (frontend stores LOCALE as a cookie).
    """
    cookie = request.cookies.get("LOCALE")
    if cookie in ("en", "ar"):
        return cookie
    accept = request.headers.get("accept-language", "")
    return "ar" if accept.lower().startswith("ar") else "en"


@router.post("/steps/{step_id}/test")
def step_test(step_id: int, request: Request, db: Session = Depends(get_db),
              current_user=Depends(get_current_user)):
    """Generate a targeted step test synchronously from the seeded bank.

    Calls step_test_service.generate_step_test (bank-first, deterministic, no
    LLM on the request path); AI quiz enrichment, when opted in, runs on a
    background thread and streams ai_step_quiz_ready over SSE. Consumed by the
    learn-page QuizRunner (additive endpoint). The response is enriched with
    top-level `difficulty` and `level` (the level used = step.current_level)
    for the learn-page to display calibration."""
    payload, error, status = step_test_service.generate_step_test(
        db, current_user.id, step_id, _locale_from_request(request))
    if error:
        raise HTTPException(status_code=status, detail=error)
    step = lrepo.get_step(db, step_id)
    payload["difficulty"] = payload["skill"]["effective_difficulty"]
    payload["level"] = step.current_level if step else 1
    return payload


@router.post("/steps/{step_id}/test/submit")
def step_test_submit(step_id: int, data: StepTestSubmitIn,
                     request: Request, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    """Grade a step test, update weak points + proficiency, complete on pass.

    Calls step_test_service.grade_step_test; reuses learning_service.complete_step
    when the learner passes, and persists the graded `next_level` onto the step's
    current_level (R-C: no AI gating here). Consumed by the learn-page QuizRunner.
    """
    result, error, status = step_test_service.grade_step_test(
        db, current_user.id, step_id,
        {"assessment_id": data.assessment_id, "answers": data.answers},
        _locale_from_request(request))
    if error:
        raise HTTPException(status_code=status, detail=error)
    next_level = result.get("next_level")
    if next_level is not None:
        lrepo.update_step_current_level(db, step_id, next_level)
    return result


@router.get("/wizard-options", response_model=WizardOptionsOut)
def wizard_options(db: Session = Depends(get_db)):
    """Return wizard source data (job roles, career fields, preferences).
    Calls services/wizard_service.wizard_options; consumed by useSystemApi.useWizardOptions()."""
    return wizard_service.wizard_options(db)


def _quiz_bank(job_id: str | None) -> dict[str, list[int]] | None:
    """Resolve an AI quiz answer-key bank entry, or None.

    Helper of wizard_analysis; lazily imports routers.ai.AI_QUIZ_BANK
    (populated by _wizard_job on ai_quiz_ready) to avoid a circular
    import — routers.ai does not import this module.
    """
    if not job_id:
        return None
    from backend.routers.ai import AI_QUIZ_BANK
    return AI_QUIZ_BANK.get(job_id)


def _analysis_from_bank(skills, answers, bank, previous):
    """Grade per-skill rows against the AI quiz answer-key bank (pure).

    Helper of wizard_analysis for AI-delivered quizzes; mirrors
    _build_report_rows' row shape and weakness/strength rules but reads
    correct indices from bank[normalize_key(skill).lower()] in delivered
    question order instead of seeded assessment questions. Skills with
    no delivered questions keep total=0 and their previous level.
    """
    rows, weak, strong = [], [], []
    for s in skills:
        key = normalize_key(s.name).lower()
        truth = bank.get(key, [])
        keyed = [(i, answers[k])
                 for i, _ in enumerate(truth)
                 for k in [f"{key}_q{i}"]
                 if k in answers]
        correct = sum(1 for i, v in keyed if v == truth[i])
        total, ans_n = len(truth), len(keyed)
        prev = previous.get(s.name, 0)
        lvl = max(0, min(5, round(correct / total * 5))) if total else prev
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


def _attach_narrative(report: dict, per_skill: list, locale: str = "en",
                      topics: list = None) -> None:
    """Enrich a results report with the AI narrative when allowed.

    Callee of wizard_analysis; gated on settings.AI_ENABLED +
    llm_pipeline._engine_available, calls analyze_diagnostic and flips
    narrative_available only on success (mutates report in place). New
    optional params focus recommendations on topics and select output
    locale for the generated narrative.
    """
    if settings_service.is_ai_enabled() and llm_pipeline._engine_available():
        narrative = llm_pipeline.analyze_diagnostic(
            per_skill, topics=topics, locale=locale)
        if narrative:
            report.update(narrative=narrative, narrative_available=True)


@router.post("/wizard/analysis")
def wizard_analysis(data: WizardAnalysisIn, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    """Phase-1 detailed results BEFORE path creation (SS-AI spec).

    Grades via learning_service._score_answers(persist=False) +
    _build_report_rows, or purely through _analysis_from_bank when
    data.quiz_job_id resolves in routers.ai.AI_QUIZ_BANK; optionally
    enriches via _attach_narrative. Performs ZERO writes. Consumed by
    PathWizard ResultsStep (frontend Task 10).
    """
    role = catalog_repository.get_job_role_by_title(db, data.goal)
    if not role:
        raise HTTPException(status_code=404, detail="Unknown job role")
    skills = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    if not skills:
        raise HTTPException(status_code=404, detail="Role has no skills")
    previous = arepo.get_skill_profile(db, current_user.id)
    bank = _quiz_bank(data.quiz_job_id)
    if bank is not None:
        per_skill, weaknesses, strengths = _analysis_from_bank(
            skills, data.answers or {}, bank, previous)
        below = [s for s, row in zip(skills, per_skill)
                 if row["assessed_level"] < MASTERY_LEVEL]
    else:
        levels = learning_service._score_answers(
            db, skills, data.answers or {}, current_user.id, persist=False)
        per_skill, weaknesses, strengths = _build_report_rows(
            db, skills, data.answers or {}, levels, previous)
        below = [s for s in skills if levels[s.id] < MASTERY_LEVEL]
    hours = sum((s.estimated_hours or 10) for s in below)
    report = {
        "per_skill": per_skill, "weaknesses": weaknesses,
        "strengths": strengths,
        "recommended_focus": weaknesses[:5],
        "estimated_weeks": max(1, round(hours / max(data.weekly_hours, 1))),
        "narrative": None, "narrative_available": False,
    }
    _attach_narrative(report, per_skill, locale=data.locale or "en",
                      topics=[t for s in skills for t in (s.topics or [])])
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
