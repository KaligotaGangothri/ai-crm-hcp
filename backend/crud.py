from sqlalchemy.orm import Session
from models import Interaction
from datetime import datetime

def create_interaction(db: Session, data: dict):
    """
    Creates a new HCP interaction record.
    Includes data sanitization to handle AI-generated lists for topics and followups.
    """
    # 1. Safely handle 'topics' if the AI returns a list or string
    topics = data.get("topics", "")
    if isinstance(topics, list):
        topics = ", ".join(topics)
        
    # 2. Safely handle 'followups' if the AI returns a list or string
    followups = data.get("followups", "")
    if isinstance(followups, list):
        followups = ", ".join(followups)

    # 3. Map dictionary data to the SQLAlchemy Interaction model
    obj = Interaction(
        doctor_name=data.get("doctor_name", "Unknown"),
        interaction_type=data.get("interaction_type", "Meeting"),
        topics=topics,
        sentiment=data.get("sentiment", "neutral"),
        followups=followups,
        created_at=str(datetime.now())
    )
    
    # 4. Commit to SQLite
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_interactions(db: Session):
    """
    Retrieves all interactions, ordered by the most recent first.
    """
    return db.query(Interaction).order_by(Interaction.id.desc()).all()

def update_last_interaction(db: Session, sentiment_update: str):
    """
    TOOL HELPER: Finds the most recent interaction and updates its sentiment.
    This is used by the LangGraph 'Edit' tool for seamless chat-based updates.
    """
    last_interaction = db.query(Interaction).order_by(Interaction.id.desc()).first()
    if last_interaction:
        last_interaction.sentiment = sentiment_update
        db.commit()
        db.refresh(last_interaction)
    return last_interaction

def update_interaction(db: Session, id: int, updates: dict):
    """
    Generic update function to modify specific fields of a record by ID.
    """
    obj = db.query(Interaction).filter(Interaction.id == id).first()
    if obj:
        for k, v in updates.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj