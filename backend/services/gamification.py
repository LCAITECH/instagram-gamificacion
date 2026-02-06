from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from .. import models, schemas
from datetime import datetime
from . import sheets_sync
import os

# Rank Constants
RANK_NOVATO = "Novato de Aluminio ✨"
# Secret Code for Validating Joins (e.g. "CRYPTO_2026_LCA")
SECRET_CODE = os.getenv("SECRET_CODE", "CRYPTO_2026_LCA")

def get_or_create_user(db: Session, username: str, full_name: str = "Unknown") -> models.User:
    user = db.query(models.User).filter(models.User.instagram_username == username).first()
    if not user:
        user = models.User(
            instagram_username=username,
            full_name=full_name,
            rank=RANK_NOVATO, # Default rank
            loyalty_score=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def process_interaction(db: Session, data: schemas.WebhookInteraction, bg_tasks: BackgroundTasks):
    user = get_or_create_user(db, data.instagram_username)
    
    points_to_add = 0
    reason = ""
    
    # Logic: If SendPulse sends a "correct_answer", we check against it.
    # If not, we assume any participation is +2, unless specific hardcoded logic exists.
    
    is_correct = False
    if data.correct_answer:
        if data.answer.strip().lower() == data.correct_answer.strip().lower():
            is_correct = True
    
    # Fallback for old hardcoded "Liquidity" flow if needed, or generic
    if is_correct:
        points_to_add = 5
        reason = f"{data.category}: Correct Answer"
    else:
        points_to_add = 1
        reason = f"{data.category}: Participation ({data.answer})"
        
    # Update User
    user.loyalty_score += points_to_add
    user.main_interest = data.category # Update interest based on latest interaction
    
    # Log Transaction
    trx = models.Transaction(
        user_id=user.id,
        points_change=points_to_add,
        reason=reason
    )
    
    db.add(trx)
    db.commit()
    db.refresh(user)
    
    # Trigger Sync
    bg_tasks.add_task(sheets_sync.sync_user_to_sheets, user.id)
    
    return user

def process_onboarding(db: Session, data: schemas.WebhookOnboarding, bg_tasks: BackgroundTasks):
    user = get_or_create_user(db, data.instagram_username, data.full_name)
    
    # If user is new (score < 1), give welcome bonus
    if user.loyalty_score < 1:
        user.loyalty_score += 3
        user.rank = RANK_NOVATO
        
        trx = models.Transaction(
            user_id=user.id,
            points_change=3,
            reason="Onboarding: Welcome Bonus"
        )
        db.add(trx)
        if data.telegram_id:
            user.telegram_id = data.telegram_id
            
        db.commit()
        
    # Trigger Sync (Always sync on onboarding potential change)
    bg_tasks.add_task(sheets_sync.sync_user_to_sheets, user.id)
        
    return user

def validate_code(db: Session, data: schemas.WebhookValidation):
    if data.secret_code != SECRET_CODE:
        return {"success": False, "message": "Invalid Code"}
        
    user = get_or_create_user(db, data.instagram_username)
    
    # Check if already validated? (Optional: prevent double dip)
    # For now, just return success + points if we want?
    # User requirement: "Validate ... before adding points". 
    # Let's assume validation itself might give points or just enable future ones.
    # For this snippet, we just return success.
    
    return {"success": True, "message": "Code Validated", "current_score": user.loyalty_score}
