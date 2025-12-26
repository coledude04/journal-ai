"""
Business logic for user logs calendar management.
Orchestrates calendar month retrieval and user logs updates.
"""
from datetime import date
from models.logs import CalendarMonthsResponse
from db.user_logs_repo import (
    list_calendar_months as db_list_calendar_months,
    update_user_collection_with_log as db_update_user_collection_with_log,
    update_user_collection_with_feedback as db_update_user_collection_with_feedback,
)


def list_calendar_months(user_id: str, startYear: int, startMonth: int, numMonths: int) -> CalendarMonthsResponse:
    """
    Retrieve calendar months for a user with log and feedback information.
    Pure pass-through to database layer.
    """
    return db_list_calendar_months(
        user_id=user_id,
        startYear=startYear,
        startMonth=startMonth,
        numMonths=numMonths,
    )


def update_user_collection_with_log(user_id: str, new_log_id: str, log_date: date) -> None:
    """
    Update user's logs collection when a new log is created.
    Pure pass-through to database layer.
    """
    return db_update_user_collection_with_log(
        user_id=user_id,
        new_log_id=new_log_id,
        log_date=log_date,
    )


def update_user_collection_with_feedback(user_id: str, log_date: date) -> None:
    """
    Update user's logs collection when feedback is generated for a log.
    Pure pass-through to database layer.
    """
    return db_update_user_collection_with_feedback(
        user_id=user_id,
        log_date=log_date,
    )
