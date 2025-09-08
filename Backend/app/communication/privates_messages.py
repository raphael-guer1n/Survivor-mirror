from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.communication.com_classes import Message, Read_message, Read_conversation_from
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
        cursor.execute("SELECT id FROM users where email = %s",
            (sender_email,))
        get_sender = cursor.fetchone()
        if not get_sender:
            raise HTTPException(status_code=501,
                detail="Sender does not exist.")
        cursor.execute("SELECT id FROM users where email = %s",
            (reciver_email,))
        get_reciver = cursor.fetchone()
        if not get_reciver:
            raise HTTPException(status_code=501,
                detail="The email you tried to send this message does not exist.")
        if (get_sender == get_reciver):
            raise HTTPException(status_code=501,
                detail="Sender and Reciver of the massages cannot be the same.")
        reciver_id: int = get_reciver['id']
        sender_id: int = get_sender['id']
        cursor.execute("SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s",
            (sender_id, reciver_id, reciver_id, sender_id,))
        get_conv = cursor.fetchone()
        if not get_conv:
            cursor.execute("INSERT INTO conversations (user1_id, user2_id) VALUES (%s, %s)",
                (sender_id, reciver_id,))
            connection.commit()
            cursor.execute("SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s",
                (sender_id, reciver_id, reciver_id, sender_id,))
            get_conv = cursor.fetchone()
        conv_id: int = get_conv['id']
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender_id, receiver_id, content) VALUES (%s, %s, %s, %s)",
            (conv_id, sender_id, reciver_id, message.content_message,))
        connection.commit()
        return {"sender_email": sender_email, "reciver_email": reciver_email, "content_message": message.content_message}
    finally:
        cursor.close()
        connection.close()


@comm.post("/read_conversation", response_model= list[Read_message])
def read_message(reader: Read_conversation_from):
    reader_email: str = reader.reader_email.strip().lower()
    readed_email: str= reader.chat_with_email.strip().lower()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    conversation: list[Read_message]= []
    try:
        cursor.execute("SELECT id, name FROM users where email = %s",
            (reader_email,))
        get_reader = cursor.fetchone()
        if not get_reader:
            raise HTTPException(status_code=501,
                detail="Reader does not exist.")
        cursor.execute("SELECT id, name FROM users where email = %s",
            (readed_email,))
        get_readed = cursor.fetchone()
        if not get_readed:
            raise HTTPException(status_code=501,
                detail="The email you tried to read your conversation with does not exist.")
        if (get_reader == get_readed):
            raise HTTPException(status_code=501,
                detail="You cannot try to read a conversation with yourself.")
        reader_id: int = get_reader['id']
        readed_id: int = get_readed['id']
        reader_name: str = get_reader['name']
        readed_name: str = get_readed['name']
        cursor.execute(
            "SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s",
            (reader_id, readed_id, readed_id, reader_id,))
        get_conv = cursor.fetchone()
        if get_conv:
            conv_id: int = get_conv['id']
            cursor.execute("SELECT sender_id, content FROM messages where conversation_id = %s",
                (conv_id,))
            all_messages = cursor.fetchall()
            for message_s in all_messages:
                if reader_id == message_s['sender_id']:
                    conversation.append(Read_message(
                        sender_name=reader_name,
                        content=message_s['content']))
                if readed_id == message_s['sender_id']:
                    conversation.append(Read_message(
                        sender_name=readed_name,
                        content=message_s['content']))
            return conversation
        else:
            raise HTTPException(status_code=501, 
                detail="No conversation with this email yet.")
    finally:
        cursor.close()
        connection.close()
        
@comm.post("/read_message", response_model= Read_message)
def read_message(reader: Read_conversation_from):
    reader_email: str = reader.reader_email.strip().lower()
    readed_email: str= reader.chat_with_email.strip().lower()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    conversation: list[Read_message]= []
    try:
        cursor.execute("SELECT id, name FROM users where email = %s",
            (reader_email,))
        get_reader = cursor.fetchone()
        if not get_reader:
            raise HTTPException(status_code=501,
                detail="Reader does not exist.")
        cursor.execute("SELECT id, name FROM users where email = %s",
            (readed_email,))
        get_readed = cursor.fetchone()
        if not get_readed:
            raise HTTPException(status_code=501,
                detail="The email you tried to read your conversation with does not exist.")
        if (get_reader == get_readed):
            raise HTTPException(status_code=501,
                detail="You cannot try to read a conversation with yourself.")
        reader_id: int = get_reader['id']
        readed_id: int = get_readed['id']
        reader_name: str = get_reader['name']
        readed_name: str = get_readed['name']
        cursor.execute(
            "SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s",
            (reader_id, readed_id, readed_id, reader_id,))
        get_conv = cursor.fetchone()
        if get_conv:
            conv_id: int = get_conv['id']
            cursor.execute("SELECT sender_id, content FROM messages where conversation_id = %s",
                (conv_id,))
            all_messages = cursor.fetchall()
            last_message = all_messages[-1]
            if reader_id == last_message['sender_id']:
                return {"sender_name": reader_name, "content": last_message['content']}
            if readed_id == last_message['sender_id']:
                return {"sender_name": readed_name, "content": last_message['content']}

        else:
            raise HTTPException(status_code=501, 
                detail="No conversation with this email yet.")
    finally:
        cursor.close()
        connection.close()