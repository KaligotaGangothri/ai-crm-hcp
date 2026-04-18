from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph
from services.ai_service import classify_intent, extract_data, suggest_action, generate_insights

# 1. Define State explicitly so LangGraph never loses keys (This fixes the KeyError!)
class State(TypedDict, total=False):
    input: str
    output: Optional[str]
    action: Optional[str]
    data: Optional[Any]
    doctor_name: Optional[str]
    interaction_type: Optional[str]
    topics: Optional[str]
    sentiment: Optional[str]
    followups: Optional[str]

def log_node(state):
    # Safely get the input, defaulting to an empty string if missing
    user_input = state.get("input", "")
    data = extract_data(user_input)
    return data  # Returns dictionary to update state

def edit_node(state):
    return {"action": "edit", "data": state.get("input", "")}

def history_node(state):
    return {"action": "history"}

def suggest_node(state):
    return {"output": suggest_action(state.get("input", ""))}

def insight_node(state):
    return {"output": generate_insights("all interactions")}

# Setup Graph
graph = StateGraph(State)

graph.add_node("log", log_node)
graph.add_node("edit", edit_node)
graph.add_node("history", history_node)
graph.add_node("suggest", suggest_node)
graph.add_node("insight", insight_node)

# Router Logic
def route_intent(state):
    # Safely get the input here as well
    return classify_intent(state.get("input", ""))

# Set dynamic entry point based on intent
graph.set_conditional_entry_point(
    route_intent,
    {
        "log": "log",
        "edit": "edit",
        "history": "history",
        "suggest": "suggest",
        "insight": "insight",
    }
)

app = graph.compile()