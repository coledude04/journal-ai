from fastapi import APIRouter, Depends, HTTPException
from service.models.feedback import RequestFeedbackRequest, AIFeedback
from service.core.auth import get_current_user_id
from service.db.feedback_repo import request_feedback

router = APIRouter(prefix="/feedback", tags=["AI Feedback"])


@router.post("/request", response_model=AIFeedback)
def request_feedback_handler(
    payload: RequestFeedbackRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Request AI feedback for a daily log.
    """
    try:
        return request_feedback(user_id=user_id, log_id=payload.logId)
    except ValueError as e:
        if "Unauthorized" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
