from fastapi import APIRouter, Depends
from core.auth import get_current_user_id
from core.rate_limiter import check_rate_limit
from db.streaks_repo import get_streak

router = APIRouter(prefix="/streaks", tags=["Streaks"])


@router.get("")
def get_streak_handler(
    user_id: str = Depends(get_current_user_id),
):
    """
    Get the user's current and longest streak.
    """
    check_rate_limit(user_id=user_id)
    return get_streak(user_id)
