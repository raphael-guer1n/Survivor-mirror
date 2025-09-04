from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.communication.com_classes import Message, Conversation
from app.utils.security import hash_password, verify_password

comm = APIRouter(prefix="/communication", tags=["communication"])

@comm.post("/send_message", response_model=Message)
def send_message(message: Message):
    sender_email: str = message.sender_email.strip().lower()
    reciver_email: str= message.reciver_email.strip().lower()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SHOW TABLES")
    for table in cursor.fetchall():
        print(table)

    try:
        cursor.execute("SELECT id FROM users where email = %s", (sender_email,))
        get_sender = cursor.fetchone()
        if not get_sender:
            raise HTTPException(status_code=400, detail="Sender does not exist.")
        cursor.execute("SELECT id FROM users where email = %s", (reciver_email,))
        get_reciver = cursor.fetchone()
        if not get_reciver:
            raise HTTPException(status_code=400, detail="The email you tried to send this message does not exist.")
        if (get_sender == get_reciver):
            raise HTTPException(status_code=400, detail="Sender and Reciver of the massages cannot be the same.")
        reciver_id: int = get_reciver['id']
        sender_id: int = get_sender['id']
        cursor.execute("SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s", (sender_id, reciver_id, reciver_id, sender_id,))
        get_conv = cursor.fetchone()
        if not get_conv:
            cursor.execute("INSERT INTO conversations (user1_id, user2_id) VALUES (%s, %s)",(sender_id, reciver_id,))
            connection.commit()
            cursor.execute("SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s", (sender_id, reciver_id, reciver_id, sender_id,))
            get_conv = cursor.fetchone()
        conv_id: int = get_conv['id']
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender_id, receiver_id, content) VALUES (%s, %s, %s, %s)", (conv_id, sender_id, reciver_id, message.content_message,))
        connection.commit()
        return {"sender_email": sender_email, "reciver_email": reciver_email, "content_message": message.content_message}
    finally:
        cursor.close()
        connection.close()


# pour les conversations vérifier si in des id contiens les 2 ids des users.