from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .. import schemas, database
from ..services import gamification

router = APIRouter(
    prefix="/webhook",
    tags=["webhooks"]
)

@router.post("/interaction")
def webhook_interaction(data: schemas.WebhookInteraction, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    user = gamification.process_interaction(db, data, background_tasks)
    return {
        "status": "ok", 
        "new_score": user.loyalty_score,
        "new_rank": user.rank,
        "current_interest": user.main_interest
    }

@router.post("/onboarding")
def webhook_onboarding(data: schemas.WebhookOnboarding, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    user = gamification.process_onboarding(db, data, background_tasks)
    return {"status": "ok", "rank": user.rank}

@router.post("/validate")
def webhook_validate(data: schemas.WebhookValidation, db: Session = Depends(database.get_db)):
    result = gamification.validate_code(db, data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
