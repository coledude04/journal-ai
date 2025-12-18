from datetime import date, datetime, timedelta
from google.cloud.firestore_v1 import Query
from db.firestore import get_db
from db.logs_repo import COLLECTION as LOGS_COLLECTION

def get_current_streak(user_id: str) -> dict:
    """
    Calculate current streak of consecutive daily logs.
    Returns current streak count and last log date.
    """
    db = get_db()
    
    # Get all logs for the user, ordered by date descending
    docs = list(db.collection(LOGS_COLLECTION).where(
        "userId", "==", user_id
    ).order_by(
        "date", direction=Query.DESCENDING
    ).stream())
    
    if not docs:
        return {
            "currentStreak": 0,
            "lastLogDate": None,
        }
    
    # Parse dates and calculate streak
    today = date.today()
    streak = 0
    last_log_date = None
    
    for doc in docs:
        data = doc.to_dict()
        log_date = data.get("date")
        
        # Handle both string and date formats
        if isinstance(log_date, str):
            log_date = date.fromisoformat(log_date)
        
        if last_log_date is None:
            last_log_date = log_date
            # Check if the most recent log is from today or yesterday
            if log_date not in (today, today - timedelta(days=1)):
                return {
                    "currentStreak": 0,
                    "lastLogDate": last_log_date.isoformat() if last_log_date else None,
                }
            streak = 1
        else:
            # Check if this log is exactly one day before the last
            if last_log_date - timedelta(days=1) == log_date:
                streak += 1
                last_log_date = log_date
            else:
                # Streak broken
                break
    
    return {
        "currentStreak": streak,
        "lastLogDate": last_log_date.isoformat() if last_log_date else None,
    }
