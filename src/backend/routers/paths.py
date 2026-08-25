"""Paths router — wizard generation, path CRUD, step progress, dashboard.

Wires /api/generate-path, /api/paths, /api/steps, /api/progress/dashboard
and /api/wizard-options to services/learning_service.py + catalog_service.py
(Task 2). Consumed by usePathApi.ts and useSystemApi.ts.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dto.learning import (
    GeneratePathIn, PathDetailOut, PathUpdate,
    StepCompletionResponse, WizardOptionsOut,
)
from backend.events.publisher import send_event
from backend.policies.auth_policy import get_current_user
from backend.repositories import learning_repository as lrepo
from backend.services import catalog_service, learning_service

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
    Calls catalog_service.wizard_options; consumed by useSystemApi.useWizardOptions()."""
    return catalog_service.wizard_options(db)
