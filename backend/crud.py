from sqlalchemy.orm import Session
from models import Interaction
from datetime import datetime

def create_interaction(db: Session, data: dict):
    # 1. Safely handle 'topics' if the AI returns a list
    topics = data.get("topics", "")
    if isinstance(topics, list):
        topics = ", ".join(topics)
        
    # 2. Safely handle 'followups' if the AI returns a list
    followups = data.get("followups", "")
    if isinstance(followups, list):
        followups = ", ".join(followups)

    # 3. Save to database
    obj = Interaction(
        doctor_name=data.get("doctor_name", "Unknown"),
        interaction_type=data.get("interaction_type", "Meeting"),
        topics=topics,
        sentiment=data.get("sentiment", "neutral"),
        followups=followups,
        created_at=str(datetime.now())
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_interactions(db: Session):
    return db.query(Interaction).order_by(Interaction.id.desc()).all()

def update_interaction(db: Session, id: int, updates: dict):
    obj = db.query(Interaction).filter(Interaction.id == id).first()
    if obj:
        for k, v in updates.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj