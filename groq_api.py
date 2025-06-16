# groq_api.py

import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Message
from datetime import datetime
from chat_graph import graph_app_invoke


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# def get_prompt(name):
#     prompts = {
#         "Roxy": "Ты — дерзкая, уверенная в себе подруга...",
#         "Luna": "Ты — мягкая ведьма, чувствуешь энергию...",
#         "Vera": "Ты — умная феминистка, подруга силы...",
#         "Zoe": "Ты — весёлая тусовщица, всегда за движ..."
#     }
#     return prompts.get(name, "Ты — поддерживающий AI-компаньон.")

def save_message(role, user_id, assistant_name, content):
    try:
        db: Session = SessionLocal()
        msg = Message(
            user_id=user_id,
            assistant_name=assistant_name,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        db.add(msg)
        db.commit()
    except Exception as e:
        print(f"DB error on save {role}: {e}")
        db.rollback()
    finally:
        db.close()

def get_groq_response(request_data):
    try:
        result = graph_app_invoke(request_data)

        assistant_reply = result.get("response", "⚠️ Ошибка в LangGraph")
        return {
            "status": "success",
            "response": assistant_reply
        }
    except Exception as e:
        return {
            "status": "error",
            "response": "⚠️ Что-то пошло не так.",
            "error": str(e)
        }
