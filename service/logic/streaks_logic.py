"""
Business logic for streak management.
"""
from datetime import date
from db.streaks_repo import get_streak, update_user_streak as db_update_user_streak


def get_user_streak(user_id: str) -> dict:
    """
    Get current streak information for a user.
    Returns current_streak, longest_streak, and last_completed_date.
    """
    return get_streak(user_id=user_id)


def update_user_streak(user_id: str, timezone: str, log_date: date) -> dict:
    """
    Update user streak after completing a log.
    Handles streak calculation logic and updates the database.
    """
    return db_update_user_streak(user_id=user_id, timezone=timezone, log_date=log_date)
