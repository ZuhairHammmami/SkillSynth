"""Wizard options service — GET /api/wizard-options payload builder.

Called by routers/paths.py; reads job roles via catalog_repository.
Response shape is frozen for wire compatibility with the frontend
useWizardOptions hook (job_roles / career_fields / preferences keys).
"""

from sqlalchemy.orm import Session

from backend.repositories import catalog_repository as repo


def wizard_options(db: Session) -> dict:
    """Build the wizard options payload grouped by career field.

    Called by routers/paths.get_wizard_options; keeps the historical
    'Other' fallback for null career_field and the fixed format/language
    literals the frontend selects from."""
    flat_roles: list[dict] = []
    career_fields: dict[str, list[dict]] = {}
    for role in repo.get_all_job_roles(db):
        field = role.career_field or "Other"
        entry = {"title": role.title, "description": role.description,
                 "career_field": field}
        flat_roles.append(entry)
        career_fields.setdefault(field, []).append(entry)
    return {
        "job_roles": flat_roles,
        "career_fields": career_fields,
        "preferences": {
            "formats": ["any", "video", "article", "course", "book"],
            "languages": ["en", "ar"],
        },
    }
