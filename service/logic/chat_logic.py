"""
Business logic for chat management.
Orchestrates chat creation, message handling, and AI response generation.
"""
from models.chat import Chat, ChatPage, ChatMessage
from db.chat_repo import (
    create_chat as db_create_chat,
    get_chat as db_get_chat,
    add_message as db_add_message,
    list_chats as db_list_chats,
    add_initial_feedback_message,
)
from db.feedback_repo import get_feedback_by_id
from db.user_repo import decrement_token
from services.gemini_service import generate_chat_response


class AIResponseError(Exception):
    """Raised when AI fails to generate a response."""
    pass


def create_chat(
    user_id: str,
    chat_name: str,
    feedback_id: str | None = None,
) -> Chat:
    """
    Create a new chat session, optionally linked to feedback.
    Validates feedback ownership and adds it as initial message if provided.
    """
    # Validate and fetch feedback if provided
    if feedback_id:
        feedback, feedback_user_id = get_feedback_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback with ID {feedback_id} does not exist")
        
        if feedback_user_id != user_id:
            raise ValueError(f"Feedback with ID {feedback_id} does not belong to the user")
    
    # Create the chat
    chat = db_create_chat(user_id=user_id, chat_name=chat_name, feedback_id=feedback_id)
    
    # Add feedback as initial message if provided
    if feedback_id and feedback:
        add_initial_feedback_message(chat_id=chat.chatId, feedback_content=feedback.content)
    
    return chat


def get_chat(user_id: str, chat_id: str) -> Chat | None:
    """Get a specific chat with all its messages."""
    return db_get_chat(user_id=user_id, chat_id=chat_id)


def list_chats(
    user_id: str,
    page_size: int = 10,
    page_token: str | None = None,
) -> ChatPage:
    """List chats for a user with pagination."""
    return db_list_chats(user_id=user_id, page_size=page_size, page_token=page_token)


def send_message(
    user_id: str,
    chat_id: str,
    message: str,
    chat_messages: list[ChatMessage],
) -> ChatMessage:
    """
    Send a message in a chat and generate AI response.
    
    Orchestrates:
    - Storing user message
    - Generating AI response
    - Storing AI response
    - Decrementing user chat tokens
    
    Returns the AI response message.
    Raises AIResponseError if AI fails to generate a response.
    """
    # Store the user message
    db_add_message(chat_id=chat_id, sender="user", message=message)
    
    # Generate and store the AI response
    ai_response = generate_chat_response(
        user_id=user_id,
        query=message,
        message_history=chat_messages,
    )
    
    if not ai_response:
        raise AIResponseError("Failed to generate AI response")
    
    assistant_message = db_add_message(
        chat_id=chat_id,
        sender="assistant",
        message=ai_response,
    )
    
    # Decrement the user's chat tokens
    try:
        decrement_token(user_id=user_id, token="chatTokens")
    except Exception as e:
        print(f"Failed to decrement chat tokens: {e}")
    
    return assistant_message
