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
GROQ_MODEL = os.getenv("GROQ_MODEL")

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

def get_groq_response(request_data):
    save_message("user", request_data.user_id, request_data.assistant_name, request_data.user_input)

    messages = [
        {"role": "system", "content": get_prompt(request_data.assistant_name)},
        {"role": "user", "content": request_data.user_input}
    ]

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "stream": False,
        "temperature": 0.9
    }

    try:
        import requests
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response_json = response.json()
        print("Full Groq API response:", response_json)
        if "choices" in response_json and response_json["choices"]:
            content = response_json["choices"][0]["message"]["content"]
            save_message("assistant", request_data.user_id, request_data.assistant_name, content)
            return content
        else:
            return f"Error: Unexpected response format: {response_json}"
    except Exception as e:
        return f"Error: {str(e)}"
