from datetime import date, datetime, timedelta, time
from zoneinfo import ZoneInfo
from fastapi import HTTPException, status

def validate_log_time(timezone: str, log_date: date):
    """
    Ensures logs are submitted between 6:00 PM on log_date 
    and 12:00 PM the next day.
    """
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    
    start_time = datetime.combine(log_date, time(18, 0), tzinfo=tz)
    end_time = datetime.combine(log_date + timedelta(days=1), time(12, 0), tzinfo=tz)
    
    if not (start_time <= now <= end_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "outside_submission_window",
                "message": f"Logs for {log_date} can only be submitted between 6:00 PM and 12:00 PM the next day.",
                "current_time_user": now.strftime("%I:%M %p")
            }
        )


def validate_feedback_time(timezone: str, log_date: date):
    """
    Ensures feedback is requested between 12:00 PM and 11:59 PM 
    on the day after the log.
    """
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    
    start_time = datetime.combine(log_date + timedelta(days=1), time(12, 0), tzinfo=tz)
    end_time = datetime.combine(log_date + timedelta(days=1), time(23, 59, 59), tzinfo=tz)
    
    if not (start_time <= now <= end_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "outside_feedback_window",
                "message": "AI feedback can only be requested between 12:00 PM and midnight on the day after the log.",
                "current_time_user": now.strftime("%I:%M %p")
            }
        )