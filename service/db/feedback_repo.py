from datetime import datetime
from service.db.firestore import get_db
from service.models.feedback import AIFeedback
from service.db.logs_repo import COLLECTION as LOGS_COLLECTION

COLLECTION = "feedback"
MODEL_VERSION = "1.0.0"

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
    now = datetime.utcnow()
    
    doc = {
        "userId": user_id,
        "logId": log_id,
        "content": content,
        "modelVersion": MODEL_VERSION,
        "createdAt": now,
    }
    
    ref.set(doc)
    
    return AIFeedback(feedbackId=ref.id, **doc)


def request_feedback(user_id: str, log_id: str) -> AIFeedback:
    """
    Request AI feedback for a log.
    Validates log ownership, generates feedback, and stores it.
    """
    db = get_db()
    
    # Verify log exists and belongs to user
    log_doc = db.collection(LOGS_COLLECTION).document(log_id).get()
    if not log_doc.exists:
        raise ValueError("Log not found")
    
    log_data = log_doc.to_dict()
    if log_data.get("userId") != user_id:
        raise ValueError("Unauthorized")
    
    # TODO: Implement free-tier limits check
    # TODO: Call LLM to generate feedback (for now, using placeholder)
    
    feedback_content = f"Feedback for your log: {log_data.get('content', '')[:50]}..."
    
    return create_feedback(
        user_id=user_id,
        log_id=log_id,
        content=feedback_content,
    )
