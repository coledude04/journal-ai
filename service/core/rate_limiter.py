from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from db.firestore import get_db

RATE_LIMITS = {
    "default": {"limit": 15, "window_seconds": 60},
    "request_feedback": {"limit": 3, "window_seconds": 86400},  # 3/day
}
COLLECTION = "rate_limits"

def check_rate_limit(
    user_id: str,
    key: str = "default",
):
    config = RATE_LIMITS[key]
    limit = config["limit"]
    window = timedelta(seconds=config["window_seconds"])

    now = datetime.now(timezone.utc)
    window_start = now - window

    doc_id = f"{user_id}:{key}"
    ref = get_db().collection(COLLECTION).document(doc_id)
    doc = ref.get()

    if not doc.exists:
        ref.set({
            "count": 1,
            "windowStart": now,
        })
        return

    data = doc.to_dict()

    if data["windowStart"] < window_start:
        ref.set({
            "count": 1,
            "windowStart": now,
        })
        return

    if data["count"] >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    ref.update({"count": data["count"] + 1})
