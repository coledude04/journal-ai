from datetime import datetime
from pydantic import BaseModel

class RequestFeedbackRequest(BaseModel):
    logId: str


class AIFeedback(BaseModel):
    feedbackId: str
    logId: str
    content: str
    modelVersion: str
    createdAt: datetime
