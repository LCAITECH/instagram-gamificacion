from pydantic import BaseModel
from typing import Optional

class WebhookInteraction(BaseModel):
    instagram_username: str
    answer: str
    category: Optional[str] = "General" # e.g., "Metals", "Trading"
    correct_answer: Optional[str] = None # SendPulse can send the "right" answer for this specific reel
    full_name: Optional[str] = "Unknown" # Allows capturing name during interaction creation

class WebhookOnboarding(BaseModel):
    instagram_username: str
    full_name: Optional[str] = "Unknown"
    telegram_id: Optional[str] = None

class WebhookValidation(BaseModel):
    instagram_username: str
    secret_code: str
