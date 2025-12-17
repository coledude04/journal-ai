from fastapi import APIRouter, Depends
from datetime import date
from service.core.auth import get_current_user_id
from service.db.streaks_repo import get_current_streak

router = APIRouter(prefix="/streaks", tags=["Streaks"])


@router.get("/current")
def get_current_streak_handler(
    user_id: str = Depends(get_current_user_id),
):
    """
    Get the current streak of consecutive daily logs.
    """
    return get_current_streak(user_id)
