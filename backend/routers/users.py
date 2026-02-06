from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.get("/{username}")
def get_user_profile(username: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.instagram_username == username).first()
    if not user:
        # Optional: Auto-create basic user or return 404
        # For a smooth UX, we return 404 and frontend handles "Join Now"
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "instagram_username": user.instagram_username,
        "full_name": user.full_name,
        "loyalty_score": user.loyalty_score,
        "rank": user.rank,
        "next_rank_points": 100, # Hardcoded for now or calculate dynamic
        "progress_percent": min((user.loyalty_score / 100) * 100, 100) # Simple logic to Silver
    }

@router.get("/missions/active")
def get_missions():
    from ..services import sheets_sync
    return sheets_sync.get_active_missions()
