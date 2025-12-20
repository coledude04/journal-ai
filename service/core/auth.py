from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.firebase import verify_token
from datetime import datetime, timezone
from models.user import User

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
    

def require_feedback_access(user: User):
    if user.plan != "paid":
        raise HTTPException(402, "Upgrade required")

    if not user.subscription_expires_at or user.subscription_expires_at < datetime.now(timezone.utc):
        raise HTTPException(402, "Subscription expired")
