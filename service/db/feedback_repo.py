import os
from datetime import datetime, timezone
from db.firestore import get_db
from models.feedback import AIFeedback
from models.logs import DailyLog
from db.logs_repo import COLLECTION as LOGS_COLLECTION
from db.logs_repo import list_logs
from db.goals_repo import list_goals
from services.gemini_service import generate_response
from core.prompts import generate_input
from core.time_validation import validate_feedback_time

COLLECTION = "feedback"

def get_feedback(user_id: str, log_id: str) -> AIFeedback | None:
    """Get feedback for a specific log"""
    db = get_db()
    docs = db.collection(COLLECTION).where(
        "logId", "==", log_id
    ).where(
        "userId", "==", user_id
    ).limit(1).stream()
    
    doc = next(docs, None)
    if not doc:
        return None
    
    data = doc.to_dict()
    return AIFeedback(feedbackId=doc.id, **data)


def create_feedback(
    user_id: str,
    log_id: str,
    content: str,
) -> AIFeedback:
    """Create AI feedback for a log"""
    db = get_db()
    
    ref = db.collection(COLLECTION).document()
    now = datetime.now(timezone.utc)
    
    doc = {
        "userId": user_id,
        "logId": log_id,
        "content": content,
        "modelVersion": os.getenv("LLM_MODEL", "gemini-2.5-flash-lite"),
        "createdAt": now,
    }
    
    ref.set(doc)
    
    return AIFeedback(feedbackId=ref.id, **doc)


def request_feedback(user_id: str, log_id: str, timezone: str) -> AIFeedback:
    """
    Request AI feedback for a log.
    Validates log ownership, generates feedback, and stores it.
    Returns existing feedback if already generated for this log.
    """
    db = get_db()
    
    # Check if feedback already exists
    existing_feedback = get_feedback(user_id=user_id, log_id=log_id)
    if existing_feedback:
        return existing_feedback
    
    # Verify log exists and belongs to user
    cur_log_doc = db.collection(LOGS_COLLECTION).document(log_id).get()
    if not cur_log_doc.exists:
        raise ValueError("Log not found")

    cur_log_data = cur_log_doc.to_dict()
    if cur_log_data.get("userId") != user_id:
        raise ValueError("Unauthorized")
    
    cur_log = DailyLog(logId=log_id, **cur_log_data)
    
    validate_feedback_time(timezone=timezone, log_date=cur_log.date)
    
    # Generate feedback
    recent_logs = list_logs(user_id=user_id, page_size=3).items
    goals = list_goals(user_id=user_id, status="in_progress").items
    input_text = generate_input(current_log=cur_log, prev_logs=recent_logs[1:], goals=goals)

    print(f"Input text for feedback generation: {input_text}")
    feedback_content = generate_response(user_id=user_id, input_text=input_text)
    if not feedback_content:
        raise Exception("Failed to generate feedback")
    
    feedback = create_feedback(
        user_id=user_id,
        log_id=log_id,
        content=feedback_content,
    )

    # Update log with aiFeedbackGenerated = True
    db.collection(LOGS_COLLECTION).document(log_id).update({"aiFeedbackGenerated": True})

    return feedback
