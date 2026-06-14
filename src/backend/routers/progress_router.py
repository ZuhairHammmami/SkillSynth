# src/backend/routers/progress_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import crud, models, schemas, auth
from backend.database import get_db

router = APIRouter()

@router.post("/steps/{step_id}/complete", response_model=schemas.StepCompletionResponse)
def complete_step(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: models.Profile = Depends(auth.get_current_user)
):
    """
    نقطة نهاية محمية لوضع علامة "مكتمل" على خطوة معينة.
    - تتأكد من أن الخطوة موجودة في قاعدة البيانات.
    - تستدعي دالة CRUD لإنشاء سجل الإكمال.
    - تعيد سجل الإكمال كتأكيد.
    """
    # تحقق أولاً من أن الخطوة المطلوبة موجودة بالفعل
    db_step = db.query(models.PathStep).filter(models.PathStep.id == step_id).first()
    if not db_step:
        raise HTTPException(status_code=404, detail="Step not found")

    # (اختياري، لكنه إجراء أمني جيد) تحقق مما إذا كانت هذه الخطوة تنتمي إلى أحد مسارات المستخدم الحالي
    # ... يمكن إضافة هذا المنطق لاحقًا لزيادة الأمان ...

    # ضع علامة "مكتمل" على الخطوة
    completion_record = crud.mark_step_as_complete(
        db=db, 
        profile_id=current_user.id, 
        step_id=step_id
    )
    
    return completion_record