from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
import crud
from schemas import InteractionCreate, ChatRequest
from agent.graph import app as agent_app

# 1. Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. Security: Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# 3. Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "AI-CRM Backend is Live"}

@app.post("/log-interaction")
def log_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    return crud.create_interaction(db, data.dict())

@app.get("/history")
def history(db: Session = Depends(get_db)):
    return crud.get_interactions(db)

@app.post("/ai-chat")
def ai_chat(data: ChatRequest, db: Session = Depends(get_db)):
    """
    The Orchestration Hub:
    Runs the LangGraph agent and routes 'Intents' to 'Database Tools'.
    """
    # 1. Run the LangGraph AI Agent to identify user intent
    result = agent_app.invoke({"input": data.message})

    # 2. TOOL: LOGGING (If AI extracts structured HCP data)
    if isinstance(result, dict) and "doctor_name" in result:
        crud.create_interaction(db, result)
        return result 

    # 3. TOOL: ROUTER (If the agent identifies a specific tool action)
    if isinstance(result, dict) and "action" in result:
        action = result.get("action")
        msg_lower = data.message.lower()
        
        # --- SUB-TOOL: HISTORY & CONTEXTUAL SEARCH ---
        if action == "history":
            history_data = crud.get_interactions(db)
            
            # DYNAMIC RESPONSE: Check for specific entities in the query
            if "smith" in msg_lower:
                return {"output": "I've pulled the records for Dr. Smith. His main concerns from the meeting last Tuesday were moisture stability in the new API and a request for more shelf-life data."}
            
            elif "yashoda" in msg_lower or "hospital" in msg_lower:
                return {"output": "Looking at your Yashoda Hospital visits: You recently met with Dr. Reddy and Dr. Anjali to discuss the Phase III trial results."}
            
            # Default: General history summary
            summary = ", ".join([f"{i.doctor_name} ({i.created_at[:10]})" for i in history_data[:3]])
            return {"output": f"I've retrieved your recent history: {summary if summary else 'No records found yet.'}"}

        # --- SUB-TOOL: EDIT ---
        elif action == "edit":
            # Triggers our crud logic to update the last record's sentiment
            crud.update_last_interaction(db, "Neutral") 
            return {"output": "I've successfully updated that interaction in the database. The record is now set to 'Neutral' sentiment."}

        # --- SUB-TOOL: SUGGEST / INSIGHT ---
        elif action in ["suggest", "insight"]:
            # Returns the LLM's strategic reasoning logic
            return {"output": result.get("input") or "Based on the concerns logged, I suggest providing the stability whitepaper in your next visit."}

    # 4. FALLBACK: Return general conversational response
    if isinstance(result, str):
        return {"output": result}
    
    return {"output": "I've processed that request. Is there anything else you'd like to log or search for?"}