from datetime import datetime, timezone
from google.cloud.firestore_v1 import Query
from db.firestore import get_db
from core.pagination import encode_page_token, decode_page_token
from models.chat import Chat, ChatMessage, ChatSummary, ChatPage

COLLECTION = "chats"
MESSAGES_SUBCOLLECTION = "messages"
FEEDBACK_COLLECTION = "feedback"


def create_chat(
    user_id: str,
    chat_name: str,
    feedback_id: str | None = None,
) -> Chat:
    """
    Create a new chat in the database.
    Pure database operation.
    """
    db = get_db()
    
    now = datetime.now(timezone.utc)

    chat_doc = {
        "userId": user_id,
        "chatName": chat_name,
        "feedbackId": feedback_id,
        "createdAt": now,
        "updatedAt": now,
    }
    
    ref = db.collection(COLLECTION).document()
    ref.set(chat_doc)
    chat_id = ref.id
    
    return Chat(
        chatId=chat_id,
        userId=user_id,
        chatName=chat_name,
        feedbackId=feedback_id,
        createdAt=now,
        updatedAt=now,
    )


def add_initial_feedback_message(chat_id: str, feedback_content: str) -> None:
    """
    Add feedback as the initial message in a chat.
    Helper function for chat creation with feedback.
    """
    db = get_db()
    now = datetime.now(timezone.utc)
    
    feedback_message_doc = {
        "sender": "assistant",
        "message": feedback_content,
        "createdAt": now,
    }
    db.collection(COLLECTION).document(chat_id).collection(MESSAGES_SUBCOLLECTION).document().set(feedback_message_doc)


def get_chat(user_id: str, chat_id: str) -> Chat | None:
    """Get a specific chat with all its messages"""
    db = get_db()
    
    chat_doc = db.collection(COLLECTION).document(chat_id).get()
    if not chat_doc.exists:
        return None
    
    chat_data = chat_doc.to_dict()
    
    # Verify the chat belongs to the user
    if chat_data.get("userId") != user_id:
        return None
    
    # Get all messages
    messages = []
    message_docs = (
        db.collection(COLLECTION)
        .document(chat_id)
        .collection(MESSAGES_SUBCOLLECTION)
        .order_by("createdAt")
        .stream()
    )
    
    for msg_doc in message_docs:
        msg_data = msg_doc.to_dict()
        messages.append(ChatMessage(messageId=msg_doc.id, **msg_data))
    
    return Chat(chatId=chat_id, messages=messages, **chat_data)


def add_message(
    chat_id: str,
    sender: str,
    message: str,
) -> ChatMessage:
    """Add a message to a chat and update chat updatedAt"""
    db = get_db()
    
    now = datetime.now(timezone.utc)
    
    message_doc = {
        "sender": sender,
        "message": message,
        "createdAt": now,
    }
    
    # Add message to subcollection with auto-generated ID
    ref = (
        db.collection(COLLECTION)
        .document(chat_id)
        .collection(MESSAGES_SUBCOLLECTION)
        .document()
    )
    ref.set(message_doc)
    message_id = ref.id
    # Update chat's updatedAt timestamp
    db.collection(COLLECTION).document(chat_id).update({
        "updatedAt": now,
    })
    
    return ChatMessage(messageId=message_id, **message_doc)


def list_chats(
    user_id: str,
    page_size: int = 10,
    page_token: str | None = None,
) -> ChatPage:
    """List chats for a user with pagination"""
    db = get_db()
    
    query = (
        db.collection(COLLECTION)
        .where("userId", "==", user_id)
        .order_by("updatedAt", direction=Query.DESCENDING)
        .limit(page_size)
    )
    
    # Apply pagination token if provided
    if page_token:
        cursor = decode_page_token(page_token)
        query = query.start_after({
            "updatedAt": cursor["updatedAt"],
            "__name__": cursor["docId"]
        })
    
    docs = list(query.stream())
    
    chat_summaries = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        chat_summaries.append(ChatSummary(chatId=doc.id, **data))
    
    next_page_token = None
    if len(docs) == page_size:
        last = docs[-1]
        next_page_token = encode_page_token({
            "updatedAt": last.get("updatedAt"),
            "docId": last.id
        })
    
    return ChatPage(items=chat_summaries, nextPageToken=next_page_token)
