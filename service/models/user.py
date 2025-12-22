from datetime import date, datetime
from pydantic import BaseModel
from typing import Literal

class User(BaseModel):
    userId: str

    # streaks
    current_streak: int = 0
    last_completed_date: date | None = None
    longest_streak: int = 0
    timezone: str = "America/Chicago"

    # billing
    plan: Literal["free", "paid"] = "free"
    subscription_status: Literal["active", "canceled", "expired", "none"] = "none"
    subscription_expires_at: datetime | None = None
    chatTokens: int = 0
    feedbackTokens: int = 0

    last_revenuecat_sync: datetime | None = None

    def to_dict_firestore(self):
        return {
            # exclude userId from the dictionary
            # "userId": self.userId,
            "current_streak": self.current_streak,
            "last_completed_date": self.last_completed_date,
            "longest_streak": self.longest_streak,
            "timezone": self.timezone,
            "plan": self.plan,
            "subscription_status": self.subscription_status,
            "subscription_expires_at": self.subscription_expires_at,
            "chatTokens": self.chatTokens,
            "feedbackTokens": self.feedbackTokens,
            "last_revenuecat_sync": self.last_revenuecat_sync
        }
