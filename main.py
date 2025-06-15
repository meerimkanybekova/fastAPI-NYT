from fastapi import FastAPI
from pydantic import BaseModel
from groq_api import get_groq_response

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    assistant_name: str
    user_input: str

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    response = get_groq_response(req)
    return {"response": response}
