"""
Business logic for AI feedback management.
Orchestrates feedback generation with log and goal data.
"""
from models.feedback import AIFeedback
from db.feedback_repo import (
    get_feedback as db_get_feedback,
    create_feedback as db_create_feedback,
    request_feedback as db_request_feedback,
)


def get_feedback(user_id: str, log_id: str) -> AIFeedback | None:
    """Get feedback for a specific log."""
    return db_get_feedback(user_id=user_id, log_id=log_id)


def request_feedback(user_id: str, log_id: str, timezone: str) -> AIFeedback:
    """
    Request AI feedback for a log.
    
    Orchestrates:
    - Checking for existing feedback
    - Validating log ownership
    - Gathering context (recent logs, goals)
    - Generating feedback
    - Updating log and user_logs collection
    """
    return db_request_feedback(user_id=user_id, log_id=log_id, timezone=timezone)
