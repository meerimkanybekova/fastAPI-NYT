from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    assistant_name: str
    user_input: str
