from db.firestore import get_db
from models.user import User
from typing import Literal
from google.cloud import firestore

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
    new_user = User(userId=user_id)

    db.collection(COLLECTION).document(user_id).set(new_user.to_dict_firestore())
    return new_user


def decrement_token(user_id: str, token: Literal["chatTokens", "feedbackTokens"]) -> None:
    db = get_db()
    user_ref = db.collection(COLLECTION).document(user_id)
    
    user_ref.update({
        token: firestore.Increment(-1)
    })