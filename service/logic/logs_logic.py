"""
Business logic for logs management.
Orchestrates log operations with related updates (streaks, embeddings, user_logs).
"""
from datetime import date
from models.logs import DailyLog, DailyLogPage, DailyLogByIdResponse
from db.logs_repo import (
    list_logs as db_list_logs,
    create_log as db_create_log,
    update_log as db_update_log,
    get_log_by_id as db_get_log_by_id,
    get_log_by_date as db_get_log_by_date,
)
from db.streaks_repo import update_user_streak
from db.user_logs_repo import update_user_collection_with_log


def list_logs(
    user_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    page_size: int = 31,
    page_token: str | None = None,
) -> DailyLogPage:
    """List logs for a user with optional filtering and pagination."""
    return db_list_logs(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page_size=page_size,
        page_token=page_token,
    )


def get_log_by_id(user_id: str, log_id: str) -> DailyLogByIdResponse:
    """Get a specific log by ID with its feedback if available."""
    return db_get_log_by_id(user_id=user_id, log_id=log_id)


def get_log_by_date(user_id: str, date: date) -> DailyLog | None:
    """Get a log by date."""
    return db_get_log_by_date(user_id=user_id, date=date)


def create_log(
    user_id: str,
    date: date,
    content: str,
    user_timezone: str,
) -> DailyLog:
    """
    Create a new log and orchestrate related updates.
    
    Creates the log, updates user streak, and updates user_logs collection.
    Failures in streak or user_logs updates are logged but don't fail the operation.
    """
    # Create the log
    log = db_create_log(
        user_id=user_id,
        date=date,
        content=content,
        user_timezone=user_timezone,
    )
    
    # Update user streak
    try:
        update_user_streak(user_id=user_id, timezone=user_timezone, log_date=date)
    except Exception as e:
        # Streak update failure shouldn't fail the log creation
        print(f"Warning: Failed to update streak: {e}")
    
    # Update user_logs_collection
    try:
        update_user_collection_with_log(user_id=user_id, new_log_id=log.logId, log_date=log.date)
    except Exception as e:
        print(f"Warning: Failed to updated user_logs collection: {e}")
    
    return log


def update_log(
    user_id: str,
    log_id: str,
    content: str,
) -> DailyLog:
    """Update an existing log's content."""
    return db_update_log(user_id=user_id, log_id=log_id, content=content)
