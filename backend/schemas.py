from pydantic import BaseModel
from typing import Optional

class InteractionCreate(BaseModel):
    doctor_name: str
    interaction_type: str
    topics: Optional[str] = None
    sentiment: Optional[str] = "neutral"
    followups: Optional[str] = None

class ChatRequest(BaseModel):
    message: str