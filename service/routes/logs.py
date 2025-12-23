from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import date
from models.logs import (
    DailyLog,
    DailyLogPage,
    CreateDailyLogRequest,
    UpdateDailyLogRequest,
    CalendarMonthsResponse,
    DailyLogByIdResponse
)
from core.auth import get_current_user_id
from core.rate_limiter import check_rate_limit
from core.time_validation import validate_log_time
from db.logs_repo import list_logs, create_log, update_log, get_log_by_id
from db.streaks_repo import update_user_streak
from db.user_logs_repo import list_calendar_months, update_user_collection_with_log

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("", response_model=DailyLogPage)
def get_logs_handler(
    startDate: date | None = None,
    endDate: date | None = None,
    pageSize: int = Query(20, le=100),
    pageToken: str | None = None,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
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


@router.get("/{logId}", response_model=DailyLogByIdResponse, status_code=status.HTTP_200_OK)
def get_log_by_id_handler(
    logId: str,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)   

    try:                               
        return get_log_by_id(user_id=user_id, log_id=logId)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=DailyLog, status_code=status.HTTP_201_CREATED)
def create_log_handler(
    payload: CreateDailyLogRequest,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
    validate_log_time(timezone=payload.timezone, log_date=payload.date)
    try:
        log = create_log(
            user_id=user_id,
            date=payload.date,
            content=payload.content,
            user_timezone=payload.timezone,
        )
        
        # Update user streak (default to America/Chicago if timezone not provided)
        timezone = getattr(payload, "timezone", "America/Chicago")
        try:
            update_user_streak(user_id=user_id, timezone=timezone, log_date=payload.date)
        except Exception as e:
            # Streak update failure shouldn't fail the log creation
            print(f"Warning: Failed to update streak: {e}")

        # Update user_logs_collection
        try:
            update_user_collection_with_log(user_id=user_id, new_log_id=log.logId, log_date=log.date)
        except Exception as e:
            print(f"Warning: Failed to updated user_logs collection: {e}")
        
        return log
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{logId}", response_model=DailyLog)
def update_log_handler(
    logId: str,
    payload: UpdateDailyLogRequest,
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
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
    

@router.get("/calendar/months", response_model=CalendarMonthsResponse)
def get_calendar_months(
    startYear: int = Query(),
    startMonth: int = Query(..., ge=1, le=12),
    numMonths: int = Query(3, ge=1, le=12),
    user_id: str = Depends(get_current_user_id),
):
    check_rate_limit(user_id=user_id)
    
    return list_calendar_months(user_id=user_id, startYear=startYear, startMonth=startMonth, numMonths=numMonths)