from datetime import datetime
from google.cloud.firestore_v1 import Query
from db.firestore import get_db
from core.pagination import encode_page_token, decode_page_token
from models.logs import DailyLog, DailyLogPage

COLLECTION = "logs"

def list_logs(
    user_id: str,
    start_date=None,
    end_date=None,
    page_size: int = 20,
    page_token: str | None = None,
) -> DailyLogPage:
    db = get_db()
    query = (
        db.collection(COLLECTION)
        .where("userId", "==", user_id)
        .order_by("date", direction=Query.DESCENDING)
        .order_by("__name__", direction=Query.DESCENDING)
        .limit(page_size)
    )

    if start_date:
        query = query.where("date", ">=", start_date.isoformat())
    if end_date:
        query = query.where("date", "<=", end_date.isoformat())

    if page_token:
        cursor = decode_page_token(page_token)
        query = query.start_after({
            "date": cursor["date"],
            "__name__": cursor["docId"]
        })

    docs = list(query.stream())

    items = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        items.append(DailyLog(
            logId=doc.id,
            **data
        ))

    next_token = None
    if len(docs) == page_size:
        last = docs[-1]
        next_token = encode_page_token({
            "date": last.get("date"),
            "docId": last.id
        })

    return DailyLogPage(items=items, nextPageToken=next_token)


def create_log(user_id: str, date, content: str) -> DailyLog:
    db = get_db()

    # Enforce one log per day
    existing = (
        db.collection(COLLECTION)
        .where("userId", "==", user_id)
        .where("date", "==", date.isoformat())
        .limit(1)
        .stream()
    )
    if next(existing, None):
        raise ValueError("Log already exists")

    now = datetime.utcnow()
    ref = db.collection(COLLECTION).document()

    doc = {
        "userId": user_id,
        "date": date.isoformat(),
        "content": content,
        "createdAt": now,
        "updatedAt": now,
        "aiFeedbackGenerated": False,
    }

    ref.set(doc)

    return DailyLog(logId=ref.id, **doc)


def update_log(user_id: str, log_id: str, content: str) -> DailyLog:
    db = get_db()
    ref = db.collection(COLLECTION).document(log_id)
    
    doc = ref.get()
    if not doc.exists:
        raise ValueError("Log not found")
    
    data = doc.to_dict()
    if data.get("userId") != user_id:
        raise ValueError("Unauthorized")
    
    now = datetime.utcnow()
    updates = {
        "content": content,
        "updatedAt": now,
    }
    
    ref.update(updates)
    data.update(updates)
    
    return DailyLog(logId=log_id, **data)
