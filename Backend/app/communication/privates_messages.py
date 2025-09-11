from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.communication.com_classes import Message, Read_message, Read_conversation_from

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
def read_conversation(reader: Read_conversation_from):
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
        
@comm.get("/read_message/{reader_email}/with/{readed_email}", response_model= Read_message)
def read_message_from_email(reader_email :str, readed_email: str):
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
             
@comm.get("/read_conversation/{reader_email}/with/{readed_email}", response_model= list[Read_message])
def read_conversation_by_emils(reader_email: str, readed_email: str):
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

@comm.get("/get_conversations_id/{user_id}", response_model= list[int])
def get_conversation_id(user_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    conversation: list[int]= []
    try:
        cursor.execute(
            "SELECT id FROM conversations where user1_id = %s OR user2_id = %s", (user_id, user_id))
        get_conv = cursor.fetchall()
        if get_conv:
            for convs in get_conv:
                    conversation.append(convs['id'])
            return conversation
        else:
            raise HTTPException(status_code=501, 
                detail="No conversation with this email yet.")
    finally:
        cursor.close()
        connection.close()

@comm.get("/read_conversation/{conversation_id}", response_model= list[Read_message])
def read_conversation_by_id(conversation_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    user_one_id: int
    user_two_id: int
    user_one: str = ""
    user_two: str = ""
    conversation: list[Read_message]= []
    try:
        cursor.execute(
            "SELECT user1_id, user2_id FROM conversations where id = %s", (conversation_id,))
        users = cursor.fetchone()
        user_one_id = users['user1_id']
        user_two_id = users['user2_id']
        cursor.execute("SELECT email, name FROM users where id = %s", (user_one_id,))
        get_reader = cursor.fetchone()
        if not get_reader:
            raise HTTPException(status_code=501,
                detail="Reader does not exist.")
        cursor.execute("SELECT email, name FROM users where id = %s", (user_two_id,))
        get_readed = cursor.fetchone()
        if not get_readed:
            raise HTTPException(status_code=501,
                detail="The email you tried to read your conversation with does not exist.")
        if (get_reader == get_readed):
            raise HTTPException(status_code=501,
                detail="You cannot try to read a conversation with yourself.")
        user_one_name: int = get_reader['name']
        user_two_name: int = get_readed['name']
        user_one: str = get_reader['email']
        user_two: str = get_readed['email']
        cursor.execute("SELECT sender_id, content FROM messages where conversation_id = %s",
            (conversation_id,))
        all_messages = cursor.fetchall()
        for message_s in all_messages:
            if user_one_id == message_s['sender_id']:
                conversation.append(Read_message(
                    sender_name=user_one,
                    content=message_s['content']))
            if user_two_id == message_s['sender_id']:
                conversation.append(Read_message(
                    sender_name=user_two,
                    content=message_s['content']))
        return conversation
    finally:
        cursor.close()
        connection.close()

@comm.get("/read_last_message_by_id/{id}/user/{user}", response_model= Read_message)
def read_last_message(id: int, user: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    email: str
    i = -1
    try:
        cursor.execute("SELECT ALL user1_id, user2_id FROM conversations",)
        all_messages = cursor.fetchall()
        for mess in all_messages:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa", mess)
        cursor.execute("SELECT user1_id, user2_id FROM conversations where id = %s",
            (id,))
        last_message = cursor.fetchone()
        print("nous avons pris :", last_message['user1_id'], last_message['user2_id'], " de ", id)
        if (last_message['user1_id'] == user):
            cursor.execute("SELECT email FROM users where id = %s",
            (last_message['user2_id'],))
            last_mess = cursor.fetchone()
            print("le push", last_mess['email'])
            return {"sender_name": last_mess['email'], "content": ""}
        cursor.execute("SELECT email FROM users where id = %s",
            (last_message['user1_id'],))
        last_mess = cursor.fetchone()
        print("le push", last_mess['email'])
        return {"sender_name": last_mess['email'], "content": ""}
    finally:
        cursor.close()
        connection.close()
        
@comm.get("/send_message/sender/{sender_email}/reciver/{reciver_email}/content/{content}/conv/{id}", response_model= None)
def add_message_to_conversation(sender_email: str, reciver_email:str, content:str, id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT user1_id, user2_id, id FROM conversations where id = %s",
            (id,))
        get_conv = cursor.fetchone()
        ##if not get_conv:
        ##    cursor.execute("INSERT INTO conversations (user1_id, user2_id) VALUES (%s, %s)",
        ##        (sender_email, reciver_email,))
        ##    connection.commit()
        ##    cursor.execute("SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s",
        ##        (sender_email, reciver_email, reciver_email, sender_email,))
        ##    get_conv = cursor.fetchone()
        conv_id: int = get_conv['id']
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
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender_id, receiver_id, content) VALUES (%s, %s, %s, %s)",
            (conv_id, sender_id, reciver_id, content,))
        connection.commit()
        print("arrivés au bout\n")
        return
    finally:
        cursor.close()
        connection.close()

@comm.get("/create_conversation/user/{user_id}/chat_with/{user_email}", response_model= None)
def create_a_conversation(user_id: int, user_email: str):
    print("nous sommes dedans voilà")
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        print(user_email, user_id, "\n")
        cursor.execute("SELECT id FROM users where email = %s", (user_email,))
        get_reader = cursor.fetchone()
        if not get_reader:
            raise HTTPException(status_code=501,
                detail="Reader does not exist.")
        cursor.execute(
            "SELECT id FROM conversations where user1_id = %s AND user2_id = %s OR user1_id = %s AND user2_id = %s", (user_id, get_reader['id'], get_reader['id'], user_id))
        get_readed = cursor.fetchone()
        if get_readed:
            raise HTTPException(status_code=501,
                detail="You already have a conversation with this guy.")
        cursor.execute("INSERT INTO conversations (user1_id, user2_id) VALUES (%s, %s)",
            (user_id, get_reader['id'],))
        connection.commit()
        print(user_id, get_reader['id'])
        return 
    finally:
        cursor.close()
        connection.close()