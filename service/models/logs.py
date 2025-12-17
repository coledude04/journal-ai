from datetime import date, datetime
from pydantic import BaseModel, Field

class DailyLog(BaseModel):
    logId: str
    userId: str
    date: date
    content: str
    createdAt: datetime
    updatedAt: datetime | None = None
    aiFeedbackGenerated: bool = False


class CreateDailyLogRequest(BaseModel):
    date: date
    content: str


class UpdateDailyLogRequest(BaseModel):
    content: str


class DailyLogPage(BaseModel):
    items: list[DailyLog]
    nextPageToken: str | None = None
