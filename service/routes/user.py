from fastapi import APIRouter, Depends
from core.auth import get_current_user
from core.rate_limiter import check_rate_limit
from models.user import User

router = APIRouter(prefix="/user", tags=["User"])

@router.get("", response_model=User)
def get_user_handler(
    user: User = Depends(get_current_user),
):
    """
    Get a specific user.
    """
    check_rate_limit(user_id=user.userId)
    
    return user
