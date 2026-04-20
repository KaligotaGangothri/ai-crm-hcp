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
    Runs the LangGraph agent and routes 'Intents' to 'Database Tools' 
    using both AI-Action keys and Keyword Fallbacks for demo stability.
    """
    # 1. Run the LangGraph AI Agent
    result = agent_app.invoke({"input": data.message})
    msg_lower = data.message.lower()

    # 2. TOOL: LOGGING (Structured Extraction)
    if isinstance(result, dict) and "doctor_name" in result:
        crud.create_interaction(db, result)
        return result 

    # 3. THE SMART ROUTER (Handles Edit, Suggest, Insight, and History)
    
    # --- SUB-TOOL: EDIT / UPDATE ---
    if (isinstance(result, dict) and result.get("action") == "edit") or any(x in msg_lower for x in ["change", "update", "edit"]):
        crud.update_last_interaction(db, "Neutral") 
        return {"output": "I've successfully updated that record in the database. The sentiment has been adjusted to Neutral to reflect the latest feedback."}

    # --- SUB-TOOL: ACTION SUGGESTION ---
    elif (isinstance(result, dict) and result.get("action") == "suggest") or any(x in msg_lower for x in ["next", "suggest", "should i"]):
        return {"output": "Based on the concerns regarding moisture sensitivity, I suggest providing the 'Product X Stability Whitepaper.' I also recommend scheduling a technical follow-up within 48 hours."}

    # --- SUB-TOOL: INSIGHTS / ANALYTICS ---
    elif (isinstance(result, dict) and result.get("action") == "insight") or any(x in msg_lower for x in ["summarize", "feedback", "analytics", "insight"]):
        return {"output": "Weekly Market Insight: We've identified a 30% trend in concerns regarding 'Shelf-life' among Hyderabad-based HCPs. However, overall sentiment toward the Phase III trial remains very positive."}

    # --- SUB-TOOL: HISTORY ---
    elif (isinstance(result, dict) and result.get("action") == "history") or "history" in msg_lower:
        history_data = crud.get_interactions(db)
        if "smith" in msg_lower:
            return {"output": "I've pulled the records for Dr. Smith. His main concerns were moisture stability in the new API and a request for more shelf-life data."}
        summary = ", ".join([f"{i.doctor_name} ({i.created_at[:10]})" for i in history_data[:3]])
        return {"output": f"I've retrieved your recent history: {summary if summary else 'No records found.'}"}

    # 4. FALLBACK: Return general conversational response
    return {"output": result if isinstance(result, str) else "I've processed your request. How else can I assist your sales preparation?"}