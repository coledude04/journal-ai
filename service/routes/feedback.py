from fastapi import APIRouter, Depends, HTTPException
from models.feedback import RequestFeedbackRequest, AIFeedback
from core.auth import get_current_user_id, require_feedback_access
from core.rate_limiter import check_rate_limit
from db.feedback_repo import request_feedback, get_feedback
from service.models.user import User

router = APIRouter(prefix="/feedback", tags=["AI Feedback"])


@router.post("/request", response_model=AIFeedback)
def request_feedback_handler(
    payload: RequestFeedbackRequest,
    user: User = Depends(require_feedback_access),
):
    """
    Request AI feedback for a daily log.
    """
    check_rate_limit(user_id=user.userId, key="request_feedback")

    try:
        return request_feedback(user_id=user.userId, log_id=payload.logId)
    except ValueError as e:
        if "Unauthorized" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{log_id}", response_model=AIFeedback)
def get_feedback_handler(
    log_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get AI feedback for a specific log by logId.
    """
    check_rate_limit(user_id=user_id)
    feedback = get_feedback(user_id=user_id, log_id=log_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback
