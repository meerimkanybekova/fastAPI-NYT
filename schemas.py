from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    assistant_name: str
    thread_id: str  
    user_input: str
