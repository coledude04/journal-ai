from fastapi import APIRouter, Depends, HTTPException
from models.chat import (
    Chat,
    ChatPage,
    ChatMessage,
    CreateChatRequest,
    SendMessageRequest,
)
from core.auth import get_current_user_id, require_chat_tokens, decrement_chat_tokens
from core.rate_limiter import check_rate_limit
from db.chat_repo import (
    create_chat,
    get_chat,
    add_message,
    list_chats,
)
from models.user import User
from services.gemini_service import generate_chat_response

router = APIRouter(prefix="/chats", tags=["Chat"])


@router.post("", response_model=Chat)
def start_chat_handler(
    payload: CreateChatRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Start a new chat session.
    Optionally link to feedback via feedbackId.
    """
    check_rate_limit(user_id=user_id)
    
    try:
        chat = create_chat(
            user_id=user_id,
            chat_name=payload.chatName,
            feedback_id=payload.feedbackId,
        )
        return chat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{chat_id}", response_model=Chat)
def get_chat_handler(
    chat_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific chat with all its messages.
    """
    check_rate_limit(user_id=user_id)
    
    chat = get_chat(user_id=user_id, chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return chat


@router.post("/{chat_id}/messages", response_model=ChatMessage)
def send_message_handler(
    chat_id: str,
    payload: SendMessageRequest,
    user: User = Depends(require_chat_tokens),
):
    """
    Send a message in a chat.
    The user message is stored, and an AI response will be generated, stored, and returned.
    """
    check_rate_limit(user_id=user.userId)
    
    # Verify the chat exists and belongs to the user
    chat = get_chat(user_id=user.userId, chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Store the user message
    add_message(
        chat_id=chat_id,
        sender="user",
        message=payload.message,
    )

    # Generate and store the AI response
    ai_response = generate_chat_response(user_id=user.userId, query=payload.message, message_history=chat.messages)
    if not ai_response:
        raise HTTPException(status_code=500, detail="Failed to generate AI response")
    assistant_message = add_message(
        chat_id=chat_id,
        sender="assistant",
        message=ai_response,
    )

    # Decrement the user's chat tokens
    try:
        decrement_chat_tokens(user=user)
    except Exception as e:
        print(f"Failed to decrement chat tokens: {e}")
    
    return assistant_message


@router.get("", response_model=ChatPage)
def list_chats_handler(
    user_id: str = Depends(get_current_user_id),
    page_size: int = 10,
    page_token: str | None = None,
):
    """
    List all chats for the current user with pagination.
    Chats are ordered by most recently updated first.
    """
    check_rate_limit(user_id=user_id)
    
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="page_size must be between 1 and 100")
    
    return list_chats(
        user_id=user_id,
        page_size=page_size,
        page_token=page_token,
    )
