from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel, field_validator

class DailyLog(BaseModel):
    logId: str
    userId: str
    date: date
    content: str
    timezone: str
    createdAt: datetime
    updatedAt: datetime | None = None
    aiFeedbackGenerated: bool = False


class CreateDailyLogRequest(BaseModel):
    date: date
    content: str
    timezone: str = "America/Chicago"  # User's timezone for streak calculation

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone: {v}")
        return v


class UpdateDailyLogRequest(BaseModel):
    content: str


class DailyLogPage(BaseModel):
    items: list[DailyLog]
    nextPageToken: str | None = None
