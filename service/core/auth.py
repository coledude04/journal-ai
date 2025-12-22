from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.firebase import verify_token
from datetime import datetime, timezone
from models.user import User
from db.user_repo import get_user, update_user

security = HTTPBearer()

def get_current_user_id(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = creds.credentials
    try:
        decoded = verify_token(token)
        return decoded["uid"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
def get_current_user(user_id: str = Depends(get_current_user_id)) -> User:
    user = get_user(user_id)
    return user
    

def require_feedback_access(user: User = Depends(get_current_user)) -> User:
    if user.feedbackTokens > 0:
        return user
    
    if user.plan != "paid":
        raise HTTPException(402, "Upgrade required")

    now = datetime.now(timezone.utc)
    if not user.subscription_expires_at or user.subscription_expires_at < now:
        raise HTTPException(402, "Subscription expired")
    
    allowed_statuses = {"active", "canceled"}
    if user.subscription_status not in allowed_statuses:
        raise HTTPException(402, "Subscription inactive")
    
    return user
    

def require_chat_tokens(user: User = Depends(get_current_user)) -> User:
    if user.chatTokens <= 0:
        raise HTTPException(402, "No tokens available")
    
    return user


def decrement_chat_tokens(user: User):
    user.chatTokens -= 1
    update_user(user)


def decrement_feedback_tokens(user: User):
    user.feedbackTokens -= 1
    update_user(user)
