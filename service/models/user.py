from datetime import date, datetime
from pydantic import BaseModel
from typing import Literal

class User(BaseModel):
    userId: str

    # streaks
    current_streak: int
    last_completed_date: date | None
    longest_streak: int
    timezone: str

    # billing
    plan: Literal["free", "paid"]
    subscription_status: Literal["active", "canceled", "expired", "none"]
    subscription_expires_at: datetime | None

    last_revenuecat_sync: datetime | None
