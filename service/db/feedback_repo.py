import os
from datetime import datetime, timezone
from db.firestore import get_db
from models.feedback import AIFeedback
from models.logs import DailyLog
from db.logs_repo import COLLECTION as LOGS_COLLECTION

COLLECTION = "feedback"

def get_feedback(user_id: str, log_id: str) -> AIFeedback | None:
    """Get feedback for a specific log"""
    db = get_db()
    ref = db.collection(COLLECTION).document(log_id)

    doc = ref.get()
    if not doc.exists:
        return None
    
    data = doc.to_dict()
    if doc.get("userId") != user_id:
        raise ValueError("Unauthorized")
    
    return AIFeedback(logId=doc.id, **data)


def get_feedback_by_id(feedback_id: str) -> tuple[AIFeedback | None, str | None]:
    """
    Get feedback by ID.
    Returns (feedback, userId) tuple for validation purposes.
    Pure database operation for feedback validation.
    """
    db = get_db()
    doc = db.collection(COLLECTION).document(feedback_id).get()
    
    if not doc.exists:
        return (None, None)
    
    data = doc.to_dict()
    user_id = data.get("userId")
    return (AIFeedback(logId=doc.id, **data), user_id)


def create_feedback(
    user_id: str,
    log_id: str,
    content: str,
) -> AIFeedback:
    """Create AI feedback for a log"""
    db = get_db()
    
    ref = db.collection(COLLECTION).document(log_id)
    now = datetime.now(timezone.utc)
    
    doc = {
        "userId": user_id,
        "content": content,
        "modelVersion": os.getenv("LLM_MODEL", "gemini-2.5-flash-lite"),
        "createdAt": now,
    }
    
    ref.set(doc)
    
    return AIFeedback(logId=log_id, **doc)


def get_log_by_id_raw(log_id: str) -> tuple[DailyLog | None, bool]:
    """
    Get a log by ID without user validation.
    Pure database operation.
    Returns (log, exists) tuple.
    """
    db = get_db()
    doc = db.collection(LOGS_COLLECTION).document(log_id).get()
    
    if not doc.exists:
        return (None, False)
    
    data = doc.to_dict()
    log = DailyLog(logId=log_id, **data)
    return (log, True)


def mark_feedback_generated(log_id: str) -> None:
    """
    Mark a log as having AI feedback generated.
    Pure database operation.
    """
    db = get_db()
    db.collection(LOGS_COLLECTION).document(log_id).update({"aiFeedbackGenerated": True})
