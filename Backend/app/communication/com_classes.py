from pydantic import BaseModel

class Message(BaseModel):
    sender_email: str
    reciver_email: str
    content_message: str

class Recive_Message(BaseModel):
    reciver_id: int
    sender_id: int
    content_message: str

class Conversation(BaseModel):
    conversation_id: int
    user_1_id: int
    user_2_id: int
    last_update: float