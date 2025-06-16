from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from database import init_db, SessionLocal
from groq_api import get_groq_response  # путь к твоему файлу
from schemas import ChatRequest
import uvicorn

from sqlalchemy.orm import Session
from models import Message

app = FastAPI()
init_db() 

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        reply = get_groq_response(req)
        return {"response": reply}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

@app.get("/history")
def get_history(user_id: str = Query(...), thread_id: str = Query(...)):
    db: Session = SessionLocal()
    try:
        messages = (
            db.query(Message)
            .filter_by(user_id=user_id, thread_id=thread_id)
            .order_by(Message.timestamp)
            .all()
        )
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    finally:
        db.close()