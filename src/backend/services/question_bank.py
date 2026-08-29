"""Deterministic instant quiz delivery from the seeded assessment bank.

Primary source for the wizard placement quiz and the learner practice
tests: questions are read straight from each skill's seeded assessment
(in delivery order, so ids stay in lockstep with the seed) and returned
synchronously — no LLM, no SSE wait, no 503 gate. The LLM becomes an
optional enrichment layered on top (see routers/ai.py).

Question dicts mirror routers/assessments._questions_for_skill_id
(id="{normalized}_q<i>", skill, text, options), so /wizard/analysis and
/assessments/submit grade them with the existing (unchanged) paths.
Callers: routers/ai.py (generate_wizard_quiz, generate_practice_test);
consumes catalog_repository and assess_repository + assess_service.
"""

from backend.repositories import assess_repository as arepo
from backend.repositories import catalog_repository
from backend.services.assess_service import normalize_key


def role_quiz_bank(db, role_title: str) -> dict:
    """Synchronous role quiz from the seeded bank; every question per skill.

    Resolves the job role and its skills, then for each quiz-covered skill
    returns ALL of its seeded assessment questions in delivery order so the
    current /wizard/analysis grading (denominator == seeded question count)
    stays exact. Payload: {"questions": [...], "skills": [...]} where skills
    mirrors the wizard payload (name/difficulty/topics).
    Called by routers/ai.generate_wizard_quiz; consumes catalog_repository
    and assess_repository + assess_service.normalize_key.
    """
    role = catalog_repository.get_job_role_by_title(db, role_title)
    if not role:
        return {"questions": [], "skills": []}
    skills = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    assessments = arepo.get_assessments_for_skills(db, [s.id for s in skills])
    payload_skills = [{"name": s.name, "difficulty": s.difficulty_level or 1,
                       "topics": s.topics or []} for s in skills]
    questions: list[dict] = []
    for s in skills:
        assessment = assessments.get(s.id)
        if not assessment:
            continue
        for i, q in enumerate(arepo.get_questions(db, assessment.id)):
            questions.append({
                "id": f"{normalize_key(s.name).lower()}_q{i}",
                "skill": s.name,
                "text": q.prompt,
                "options": q.options or [],
            })
    return {"questions": questions, "skills": payload_skills}


def skill_quiz_bank(db, skill_id: int) -> dict:
    """Single-skill quiz from the seeded bank plus its seed assessment_id.

    Returns every seeded question for one skill in delivery order, along
    with the seed assessment_id so learners submit through the existing
    /assessments/submit endpoint. Payload:
    {"assessment_id", "questions": [...], "skill_id", "skill"}.
    Called by routers/ai.generate_practice_test; consumes catalog_repository,
    assess_repository and assess_service.normalize_key.
    """
    skill = catalog_repository.get_skill(db, skill_id)
    if not skill:
        return {"assessment_id": None, "questions": [], "skill_id": skill_id,
                "skill": None}
    assessment = arepo.get_assessments_for_skills(db, [skill_id]).get(skill_id)
    if not assessment:
        return {"assessment_id": None, "questions": [],
                "skill_id": skill_id, "skill": skill.name}
    questions = [{
        "id": f"{normalize_key(skill.name).lower()}_q{i}",
        "skill": skill.name,
        "text": q.prompt,
        "options": q.options or [],
    } for i, q in enumerate(arepo.get_questions(db, assessment.id))]
    return {"assessment_id": assessment.id, "questions": questions,
            "skill_id": skill_id, "skill": skill.name}
