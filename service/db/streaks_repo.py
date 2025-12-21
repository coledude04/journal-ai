from datetime import date, timedelta
from google.cloud.firestore import transactional
from db.firestore import get_db
from models.user import User

COLLECTION = "users"

def date_from_str(s: str) -> date:
    """Convert ISO format date string to date object"""
    return date.fromisoformat(s)


def get_streak(user_id: str) -> dict:
    """
    Get current streak information for a user.
    Returns current_streak, longest_streak, and last_completed_date.
    """
    db = get_db()
    doc = db.collection(COLLECTION).document(user_id).get()
    
    if not doc.exists:
        return {
            "currentStreak": 0,
            "longestStreak": 0,
            "lastCompletedDate": None,
        }
    
    data = doc.to_dict()
    return {
        "currentStreak": data.get("current_streak", 0),
        "longestStreak": data.get("longest_streak", 0),
        "lastCompletedDate": data.get("last_completed_date"),
    }


def update_streak(transaction, user_ref: str, user_data: dict, log_date: date) -> dict:
    """
    Update streak logic using transaction.
    
    Rules:
    - First ever log: current = 1
    - Same day: Do nothing
    - Yesterday: current += 1
    - Missed ≥ 1 day: current = 1
    
    Returns updated user data
    """
    last_completed_date = user_data.get("last_completed_date")
    
    if not last_completed_date:
        # First ever log
        user_data["current_streak"] = 1
    else:
        last_date = date_from_str(last_completed_date)
        
        if last_date == log_date:
            # Already counted today, return without changes
            return user_data
        elif last_date == log_date - timedelta(days=1):
            # Yesterday, increment streak
            user_data["current_streak"] = user_data.get("current_streak", 0) + 1
        else:
            # Missed ≥ 1 day, reset streak
            user_data["current_streak"] = 1
    
    # Update longest streak
    user_data["longest_streak"] = max(
        user_data.get("longest_streak", 0),
        user_data["current_streak"]
    )
    
    # Update last completed date
    user_data["last_completed_date"] = log_date.isoformat()
    
    return user_data


def update_user_streak(user_id: str, timezone: str, log_date: date) -> dict:
    """
    Update user streak after completing a log.
    Uses transactions to prevent double-counting.
    """
    db = get_db()
    transaction = db.transaction()
    user_ref = db.collection(COLLECTION).document(user_id)
    
    @transactional
    def _do_update(transaction):
        snap = user_ref.get(transaction=transaction)
        
        if not snap.exists:
            # New user
            new_user = User(userId=user_id, timezone=timezone, current_streak=1, longest_streak=1, last_completed_date=log_date)
            user_data = new_user.to_dict_firestore()
            
        else:
            user_data = snap.to_dict()
            user_data["timezone"] = timezone
            user_data = update_streak(transaction, user_ref, user_data, log_date)
        
        # Set document (creates if doesn't exist, updates if exists)
        transaction.set(user_ref, user_data, merge=True)
        
        return user_data
    
    return _do_update(transaction)
