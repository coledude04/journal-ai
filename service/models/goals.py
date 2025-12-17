from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class GoalStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"


class Goal(BaseModel):
    goalId: str
    userId: str
    text: str
    tags: list[str] = []
    status: GoalStatus
    createdAt: datetime


class CreateGoalRequest(BaseModel):
    text: str
    tags: list[str] = []


class UpdateGoalRequest(BaseModel):
    text: str | None = None
    tags: list[str] | None = None


class GoalPage(BaseModel):
    items: list[Goal]
    nextPageToken: str | None = None
