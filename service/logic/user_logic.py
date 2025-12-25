"""
Business logic for user management.
"""
from models.user import User
from db.user_repo import (
    get_user as db_get_user,
    initialize_user as db_initialize_user,
)
from typing import Literal


def get_user(user_id: str) -> User:
    """
    Get user by ID.
    Initializes a new user if they don't exist.
    """
    return db_get_user(user_id=user_id)


def initialize_user(user_id: str) -> User:
    """Initialize a new user in the system."""
    return db_initialize_user(user_id=user_id)
