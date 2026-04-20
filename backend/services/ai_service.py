import json
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

# REPLACE WITH YOUR ACTUAL GROQ API KEY
api_key = os.environ.get("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=api_key
)

def classify_intent(text):
    prompt = f"""
    Classify intent into exactly one of these words: log, edit, history, suggest, insight.
    Input: {text}
    """
    res = llm.invoke(prompt).content.strip().lower()
    for intent in ["log", "edit", "history", "suggest", "insight"]:
        if intent in res:
            return intent
    return "log"

def extract_data(text):
    # UPDATE: Added date, time, attendees, and strict formatting rules
    prompt = f"""
    You are a strict JSON generator. Extract the following fields from the text:
    doctor_name, interaction_type, date, time, attendees, topics, sentiment, followups

    Rules: 
    1. Return ONLY valid JSON. No explanation. No markdown formatting.
    2. Format 'date' as DD-MM-YYYY if possible.
    3. Format 'time' as HH:MM if possible.
    4. If any field is not mentioned in the text, return it as null.

    Text: {text}
    """
    res = llm.invoke(prompt).content.strip()
    res = res.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(res)
    except Exception as e:
        print("JSON ERROR:", res)
        # UPDATE: Added the new fields to the fallback to prevent KeyErrors
        return {
            "doctor_name": "Unknown",
            "interaction_type": "Meeting",
            "date": None,
            "time": None,
            "attendees": None,
            "topics": text,
            "sentiment": "neutral",
            "followups": ""
        }

def suggest_action(text):
    return llm.invoke(f"Suggest next action:\n{text}").content

def generate_insights(data):
    return llm.invoke(f"Analyze trends:\n{data}").content