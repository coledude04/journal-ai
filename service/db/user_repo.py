from db.firestore import get_db
from models.user import User

COLLECTION = "users"

def get_user(user_id: str) -> User:
    """Get user by ID"""
    db = get_db()
    doc = db.collection(COLLECTION).document(user_id).get()
    
    if not doc.exists:
        return initialize_user(user_id)
    
    data = doc.to_dict()
    return User(userId=doc.id, **data)


def initialize_user(user_id: str) -> User:
    """Initialize a new user"""
    db = get_db()
    user_data = {
        "timezone": "America/Chicago",
        "current_streak": 0,
        "longest_streak": 0,
        "last_completed_date": None,
        "plan": "free",
        "subscription_status": "none",
        "subscription_expires_at": None,
        "last_revenuecat_sync": None
    }

    db.collection(COLLECTION).document(user_id).set(user_data)
    return User(userId=user_id, **user_data)