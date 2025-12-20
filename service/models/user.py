from datetime import date, datetime
from pydantic import BaseModel
from typing import Literal

class User(BaseModel):
    userId: str
    current_streak: int
    last_completed_date: date
    longest_streak: int
    timezone: str
    plan: Literal["free", "paid"]
    subscription_expires_at: datetime
    last_revenuecat_sync: datetime
