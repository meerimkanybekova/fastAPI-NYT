import aiohttp
import os
import json
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Message
from datetime import datetime

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

def get_prompt(name):
    prompts = {
        "Roxy": "Ты — дерзкая, уверенная в себе подруга...",
        "Luna": "Ты — мягкая ведьма, чувствуешь энергию...",
        "Vera": "Ты — умная феминистка, подруга силы...",
        "Zoe": "Ты — весёлая тусовщица, всегда за движ..."
    }
    return prompts.get(name, "Ты — поддерживающий AI-компаньон.")

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

from chat_graph import graph_app_invoke


def get_groq_response(request_data):
    from models import Message
    from database import SessionLocal
    from sqlalchemy.orm import Session
    from datetime import datetime

    def save(role, content):
        db: Session = SessionLocal()
        try:
            msg = Message(
                user_id=request_data.user_id,
                assistant_name=request_data.assistant_name,
                role=role,
                content=content,
                timestamp=datetime.utcnow()
            )
            db.add(msg)
            db.commit()
        except Exception as e:
            print("DB error:", e)
            db.rollback()
        finally:
            db.close()

    save("user", request_data.user_input)

    # Вызов LangGraph
    result = graph_app_invoke(request_data)


    assistant_reply = result.get("response", "⚠️ Ошибка в LangGraph")
    save("assistant", assistant_reply)
    return assistant_reply
