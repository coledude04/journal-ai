from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel, field_validator

class RequestFeedbackRequest(BaseModel):
    logId: str
    timezone: str = "America/Chicago"

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone: {v}")
        return v


class AIFeedback(BaseModel):
    logId: str
    content: str
    modelVersion: str
    createdAt: datetime
