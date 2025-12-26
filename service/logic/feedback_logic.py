"""
Business logic for AI feedback management.
Orchestrates feedback generation with log and goal data.
"""
from models.feedback import AIFeedback
from db.feedback_repo import (
    get_feedback as db_get_feedback,
    create_feedback as db_create_feedback,
    get_log_by_id_raw,
    mark_feedback_generated,
)
from db.logs_repo import list_logs
from db.goals_repo import list_goals
from db.user_logs_repo import update_user_collection_with_feedback
from services.gemini_service import generate_response
from core.prompts import generate_input
from core.time_validation import validate_feedback_time


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
    # Check if feedback already exists
    existing_feedback = db_get_feedback(user_id=user_id, log_id=log_id)
    if existing_feedback:
        return existing_feedback
    
    # Verify log exists and belongs to user
    cur_log, exists = get_log_by_id_raw(log_id=log_id)
    if not exists or cur_log is None:
        raise ValueError("Log not found")
    
    if cur_log.userId != user_id:
        raise ValueError("Unauthorized")
    
    # Validate feedback timing
    validate_feedback_time(timezone=timezone, log_date=cur_log.date)
    
    # Gather context: recent logs and goals
    recent_logs = list_logs(user_id=user_id, page_size=3).items
    goals = list_goals(user_id=user_id, status="in_progress").items
    input_text = generate_input(current_log=cur_log, prev_logs=recent_logs[1:], goals=goals)
    
    # Generate feedback using AI
    print(f"Input text for feedback generation: {input_text}")
    feedback_content = generate_response(user_id=user_id, input_text=input_text)
    if not feedback_content:
        raise Exception("Failed to generate feedback")
    
    # Create and store feedback
    feedback = db_create_feedback(
        user_id=user_id,
        log_id=log_id,
        content=feedback_content,
    )
    
    # Update log with aiFeedbackGenerated flag
    try:
        mark_feedback_generated(log_id=log_id)
        update_user_collection_with_feedback(user_id=user_id, log_date=cur_log.date)
    except Exception as e:
        print(f"Failed to update 'aiFeedbackGenerated': {e}")
    
    return feedback
