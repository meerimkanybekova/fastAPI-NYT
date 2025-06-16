from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import init_db
from groq_api import get_groq_response  # путь к твоему файлу
from schemas import ChatRequest
import uvicorn

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
