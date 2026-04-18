from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
import crud
from schemas import InteractionCreate, ChatRequest
from agent.graph import app as agent_app

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "API running"}

@app.post("/log-interaction")
def log_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    return crud.create_interaction(db, data.dict())

@app.get("/history")
def history(db: Session = Depends(get_db)):
    return crud.get_interactions(db)

@app.post("/ai-chat")
def ai_chat(data: ChatRequest, db: Session = Depends(get_db)):
    # Run the LangGraph AI Agent
    result = agent_app.invoke({"input": data.message})

    # Check if the agent extracted a JSON object to log
    if isinstance(result, dict) and "doctor_name" in result:
        # Save to DB
        crud.create_interaction(db, result)
        # Return to React to auto-fill the UI
        return result

    # Fallback response
    return {"output": result}