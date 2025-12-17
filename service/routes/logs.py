from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import date
from service.models.logs import (
    DailyLog,
    DailyLogPage,
    CreateDailyLogRequest,
    UpdateDailyLogRequest
)
from service.core.auth import get_current_user_id
from service.db.logs_repo import list_logs, create_log, update_log

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("", response_model=DailyLogPage)
def get_logs_handler(
    startDate: date | None = None,
    endDate: date | None = None,
    pageSize: int = Query(20, le=100),
    pageToken: str | None = None,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return list_logs(
            user_id=user_id,
            start_date=startDate,
            end_date=endDate,
            page_size=pageSize,
            page_token=pageToken,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=DailyLog, status_code=status.HTTP_201_CREATED)
def create_log_handler(
    payload: CreateDailyLogRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return create_log(
            user_id=user_id,
            date=payload.date,
            content=payload.content,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{logId}", response_model=DailyLog)
def update_log_handler(
    logId: str,
    payload: UpdateDailyLogRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return update_log(
            user_id=user_id,
            log_id=logId,
            content=payload.content,
        )
    except ValueError as e:
        if "Unauthorized" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
