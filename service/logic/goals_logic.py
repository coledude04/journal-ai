"""
Business logic for goals management.
"""
from models.goals import Goal, GoalPage
from db.goals_repo import (
    list_goals as db_list_goals,
    create_goal as db_create_goal,
    update_goal as db_update_goal,
    delete_goal as db_delete_goal,
    complete_goal as db_complete_goal,
)


def list_goals(
    user_id: str,
    status: str = "all",
    page_size: int = 10,
    page_token: str | None = None,
) -> GoalPage:
    """List goals for a user with optional status filter and pagination."""
    return db_list_goals(
        user_id=user_id,
        status=status,
        page_size=page_size,
        page_token=page_token,
    )


def create_goal(
    user_id: str,
    text: str,
    tags: list[str],
) -> Goal:
    """Create a new goal."""
    return db_create_goal(user_id=user_id, text=text, tags=tags)


def update_goal(
    user_id: str,
    goal_id: str,
    text: str | None = None,
    tags: list[str] | None = None,
) -> Goal:
    """Update an existing goal."""
    return db_update_goal(user_id=user_id, goal_id=goal_id, text=text, tags=tags)


def delete_goal(user_id: str, goal_id: str) -> None:
    """Delete a goal."""
    db_delete_goal(user_id=user_id, goal_id=goal_id)


def complete_goal(user_id: str, goal_id: str) -> Goal:
    """Mark a goal as completed."""
    return db_complete_goal(user_id=user_id, goal_id=goal_id)
