from pydantic import BaseModel, Field
from typing import Optional

# 1. The base model WITH AI INSTRUCTIONS (Field descriptions)
class InteractionBase(BaseModel):
    doctor_name: str = Field(description="Name of the HCP or doctor, e.g., Dr. Smith")
    interaction_type: Optional[str] = Field(default="Meeting", description="Meeting, Call, or Email")
    date: Optional[str] = Field(default=None, description="The date of the meeting (e.g., 20-04-2026)")
    time: Optional[str] = Field(default=None, description="The time of the meeting (e.g., 11:11)")
    attendees: Optional[str] = Field(default=None, description="Other people present (e.g., Rahul, Akshay)")
    topics: str = Field(description="Key topics discussed, e.g., Product X efficacy")
    sentiment: Optional[str] = Field(default="neutral", description="must be exactly: positive, neutral, or negative")
    followups: Optional[str] = Field(default=None, description="Any requested follow up actions")

# 2. What main.py is looking for when creating a new record
class InteractionCreate(InteractionBase):
    pass

# 3. What is returned from the database
class Interaction(InteractionBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models

# 4. The model for incoming chat messages from React
class ChatRequest(BaseModel):
    message: str