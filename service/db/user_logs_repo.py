import calendar
from datetime import datetime, timezone, date
from db.firestore import get_db
from models.logs import CalendarMonthsResponse, CalendarMonth, CalendarDay

USER_LOGS_COLLECTION = "user_logs"

def list_calendar_months(user_id: str, startYear: int, startMonth: int, numMonths: int) -> CalendarMonthsResponse:
    months_data = []
    year, month = startYear, startMonth

    for _ in range(numMonths):
        month_data = get_or_create_month_doc(user_id=user_id, year=year, month=month)
        months_data.append(month_data)

        month += 1
        if month > 12:
            month = 1
            year += 1

    return CalendarMonthsResponse(items=months_data)


def update_user_collection_with_log(user_id: str, new_log_id: str, log_date: date) -> None:
    db = get_db()
    year, month, day = log_date.year, log_date.month, log_date.day
    doc_id = f"{user_id}-{year}-{month:02d}"
    doc_ref = db.collection(USER_LOGS_COLLECTION).document(doc_id)

    doc = doc_ref.get()
    day_index = day - 1
    if not doc.exists:
        month_model = generate_empty_month_doc(user_id, year, month)
        
        month_model.days[str(day_index)].logId = new_log_id
        month_model.days[str(day_index)].hasFeedback = False
        
        doc_ref.set(month_model.model_dump(exclude={'calendarMonthId'}, by_alias=True))
    else:
        doc_ref.update({
            f"days.{day_index}.logId": new_log_id,
            f"days.{day_index}.hasFeedback": False
        })


def update_user_collection_with_feedback(user_id: str, log_date: date):
    db = get_db()
    year, month, day = log_date.year, log_date.month, log_date.day
    doc_id = f"{user_id}-{year}-{month:02d}"
    doc_ref = db.collection(USER_LOGS_COLLECTION).document(doc_id)
    day_index = day - 1

    doc_ref.update({
        f"days.{day_index}.hasFeedback": True
    })


def get_or_create_month_doc(user_id: str, year: int, month: int) -> CalendarMonth:
    """Fetch a month document or create an empty one if it doesn't exist."""
    db = get_db()
    doc_id = f"{user_id}-{year}-{month:02d}"
    doc_ref = db.collection(USER_LOGS_COLLECTION).document(doc_id)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        monthData = CalendarMonth(
            calendarMonthId=doc.id,
            **data
        )
    else:
        monthData = generate_empty_month_doc(user_id, year, month)
    
    return monthData

def generate_empty_month_doc(user_id: str, year: int, month: int):
    doc_id = f"{user_id}-{year}-{month:02d}"

    days_in_month = calendar.monthrange(year, month)[1]
    first_weekday = date(year, month, 1).weekday()
    
    empty_days = {}
    for i in range(days_in_month):
        empty_days[str(i)] = CalendarDay(day=i + 1, logId=None, hasFeedback=False)
    
    return CalendarMonth(
        calendarMonthId=doc_id,
        year=year,
        month=month,
        firstWeekday=first_weekday, # 0 = Monday
        days=empty_days,
        createdAt=datetime.now(timezone.utc)
    )
