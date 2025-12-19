from fastapi import APIRouter, Depends, Query, status, HTTPException
from models.goals import (
    Goal,
    GoalPage,
    CreateGoalRequest,
    UpdateGoalRequest,
    GoalStatus
)
from core.auth import get_current_user_id
from core.rate_limiter import check_rate_limit
from db.goals_repo import list_goals, create_goal, update_goal, delete_goal, complete_goal

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.get("", response_model=GoalPage)
def get_goals_handler(
    status: str = Query("in_progress"),
    pageSize: int = 20,
    pageToken: str | None = None,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
    try:
        return list_goals(
            user_id=user_id,
            status=status,
            page_size=pageSize,
            page_token=pageToken,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=Goal, status_code=status.HTTP_201_CREATED)
def create_goal_handler(
    payload: CreateGoalRequest,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
    try:
        return create_goal(
            user_id=user_id,
            text=payload.text,
            tags=payload.tags,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{goalId}", response_model=Goal)
def update_goal_handler(
    goalId: str,
    payload: UpdateGoalRequest,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
    try:
        return update_goal(
            user_id=user_id,
            goal_id=goalId,
            text=payload.text,
            tags=payload.tags,
        )
    except ValueError as e:
        if "Unauthorized" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{goalId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal_handler(
    goalId: str,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
    try:
        delete_goal(user_id=user_id, goal_id=goalId)
        return None
    except ValueError as e:
        if "Unauthorized" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{goalId}/complete", response_model=Goal)
def complete_goal_handler(
    goalId: str,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
    try:
        return complete_goal(user_id=user_id, goal_id=goalId)
    except ValueError as e:
        if "Unauthorized" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
