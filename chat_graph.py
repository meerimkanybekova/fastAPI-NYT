import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Message
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

llm = ChatGroq(
    GROQ_MODEL = "llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.9
)

def get_prompt(name):
    prompts = {
        "Roxy": "Ты — дерзкая, уверенная в себе подруга, которая всегда скажет правду, даже если она колкая.  Поддерживай, но не сюсюкай. Начинай беседу с последней темы, о которой вы говорили. Не отвечай слишком длинными сообщениями. В конце оставляй вопрос, чтобы поддержать разговор.",
        "Luna": "Ты — мягкая ведьма, чувствуешь энергию собеседника. Говоришь поэтично, поддерживающе и глубоко. Не отвечай слишком длинными сообщениями.",
        "Vera": "Ты — умная феминистка, подруга силы. Мотивируй, опирайся на факты, давай уверенность. Не отвечай слишком длинными сообщениями.",
        "Zoe": "Ты — весёлая тусовщица, всегда за движ. Отвечай легко, с юмором, поддерживающе и ярко. Не отвечай слишком длинными сообщениями."
    }
    return prompts.get(name, "Ты — поддерживающий AI-компаньон. Будь доброжелательной, откликайся на эмоции пользователя.")

def fetch_chat_history(user_id, assistant_name, thread_id):
    db: Session = SessionLocal()
    try:
        messages = (
            db.query(Message)
            .filter_by(user_id=user_id, assistant_name=assistant_name, thread_id=thread_id)
            .order_by(Message.timestamp)
            .all()
        )
        history = []
        for msg in messages:
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                history.append(AIMessage(content=msg.content))
        return history
    finally:
        db.close()

def save_message(role, user_id, assistant_name, thread_id, content):
    try:
        db: Session = SessionLocal()
        msg = Message(
            user_id=user_id,
            assistant_name=assistant_name,
            thread_id=thread_id,
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


# Точка входа для вызова из groq_api.py
def graph_app_invoke(request_data):
    save_message("user", request_data.user_id, request_data.assistant_name, request_data.thread_id, request_data.user_input)

    history = fetch_chat_history(request_data.user_id, request_data.assistant_name, request_data.thread_id)
    system_msg = SystemMessage(content=get_prompt(request_data.assistant_name))
    full_messages = [system_msg] + history

    try:
        result = llm.invoke(full_messages)
        content = result.content if hasattr(result, 'content') else str(result)
        save_message("assistant", request_data.user_id, request_data.assistant_name, request_data.thread_id, content)
        return {"response": content}
    except Exception as e:
        return {"response": f"Сорри, мне надо идти. Поговорим, позже."}

