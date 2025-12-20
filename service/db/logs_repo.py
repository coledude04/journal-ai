from datetime import datetime, timezone
from typing import Any
from google.cloud.firestore_v1 import Query
from google.cloud.firestore_v1.vector import Vector
from db.firestore import get_db
from db.user_repo import get_user
from core.pagination import encode_page_token, decode_page_token
from models.logs import DailyLog, DailyLogPage
from services.embedding_service import generate_embedding

COLLECTION = "logs"
EMBEDDING_COLLECTION = "log_embeddings"

def list_logs(
    user_id: str,
    start_date=None,
    end_date=None,
    page_size: int = 31,
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
    
    # Convert date to ISO format string (YYYY-MM-DD only)
    date_str = date.isoformat() if hasattr(date, 'isoformat') else date

    # Enforce one log per day
    existing = (
        db.collection(COLLECTION)
        .where("userId", "==", user_id)
        .where("date", "==", date_str)
        .limit(1)
        .stream()
    )
    if next(existing, None):
        raise ValueError("Log already exists")

    now = datetime.now(timezone.utc)
    ref = db.collection(COLLECTION).document()

    doc = {
        "userId": user_id,
        "date": date_str,
        "content": content,
        "createdAt": now,
        "updatedAt": now,
        "aiFeedbackGenerated": False,
    }

    ref.set(doc)

    user = get_user(user_id=user_id)
    if user.plan == "paid":
        try:
            embed_log(db, user_id, ref.id, content, date_str)
        except Exception as e:
            print(f"Failed to embed log: {e}")

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
    
    now = datetime.now(timezone.utc)
    updates = {
        "content": content,
        "updatedAt": now,
    }
    
    ref.update(updates)
    data.update(updates)
    
    return DailyLog(logId=log_id, **data)


def embed_log(db: Any, user_id: str, log_id: str, log_content: str, date: str) -> None:
    print(f"Embedding log {log_id} for user {user_id}")

    log_embedding = generate_embedding(log_content)
    db.collection(EMBEDDING_COLLECTION).document(log_id).set({
        "userId": user_id,
        "embedding": Vector(log_embedding),
        "content": log_content,
        "date": date,
    })


def validate_date(date: str, timezone: str) -> bool:
    return True
