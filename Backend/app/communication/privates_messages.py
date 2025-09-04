from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.communication.com_classes import Message, Conversation
from app.utils.security import hash_password, verify_password

comm = APIRouter(prefix="/communication", tags=["communication"])

@comm.post("/send_message", response_model=Message)
def send_message(message: Message):
    sender_email = message.sender_email.strip().lower()
    reciver_email= message.reciver_email.strip().lower()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users where email = %s", (sender_email,))
        sender_id = cursor.fetchone()
        if not sender_id:
            raise HTTPException(status_code=400, detail="Sender does not exist.")
        cursor.execute("SELECT id FROM users where email = %s", (reciver_email,))
        reciver_id = cursor.fetchone()
        if not reciver_id:
            raise HTTPException(status_code=400, detail="The email you tried to send this message does not exist.")
        if (sender_id == reciver_id):
            raise HTTPException(status_code=400, detail="Sender and Reciver of the massages cannot be the same.")
        return {"sender_email": sender_email, "reciver_email": reciver_email, "content_message": message.content_message}
    finally:
        cursor.close()
        connection.close()


# pour les conversations vérifier si in des id contiens les 2 ids des users.