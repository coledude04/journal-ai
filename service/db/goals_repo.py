from datetime import datetime, timezone
from google.cloud.firestore_v1 import Query
from db.firestore import get_db
from core.pagination import encode_page_token, decode_page_token
from models.goals import Goal, GoalPage, GoalStatus

COLLECTION = "goals"

def list_goals(
    user_id: str,
    status: str = "all",
    page_size: int = 10,
    page_token: str | None = None,
) -> GoalPage:
    db = get_db()
    query = (
        db.collection(COLLECTION)
        .where("userId", "==", user_id)
        .order_by("createdAt", direction=Query.DESCENDING)
        .limit(page_size)
    )

    if status != "all":
        query = query.where("status", "==", status)

    if page_token:
        cursor = decode_page_token(page_token)
        query = query.start_after({
            "createdAt": cursor["createdAt"],
            "__name__": cursor["docId"]
        })

    docs = list(query.stream())

    items = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        items.append(Goal(goalId=doc.id, **data))

    next_token = None
    if len(docs) == page_size:
        last = docs[-1]
        next_token = encode_page_token({
            "createdAt": last.get("createdAt"),
            "docId": last.id
        })

    return GoalPage(items=items, nextPageToken=next_token)


def create_goal(
    user_id: str,
    text: str,
    tags: list[str],
) -> Goal:
    db = get_db()

    ref = db.collection(COLLECTION).document()

    doc = {
        "userId": user_id,
        "text": text,
        "tags": tags,
        "status": GoalStatus.in_progress,
        "createdAt": datetime.now(timezone.utc),
    }

    ref.set(doc)

    return Goal(goalId=ref.id, **doc)


def update_goal(
    user_id: str,
    goal_id: str,
    text: str | None = None,
    tags: list[str] | None = None,
) -> Goal:
    db = get_db()
    ref = db.collection(COLLECTION).document(goal_id)
    
    doc = ref.get()
    if not doc.exists:
        raise ValueError("Goal not found")
    
    data = doc.to_dict()
    if data.get("userId") != user_id:
        raise ValueError("Unauthorized")
    
    updates = {}
    if text is not None:
        updates["text"] = text
    if tags is not None:
        updates["tags"] = tags
    
    if updates:
        ref.update(updates)
        data.update(updates)
    
    return Goal(goalId=goal_id, **data)


def delete_goal(user_id: str, goal_id: str) -> None:
    db = get_db()
    ref = db.collection(COLLECTION).document(goal_id)
    
    doc = ref.get()
    if not doc.exists:
        raise ValueError("Goal not found")
    
    data = doc.to_dict()
    if data.get("userId") != user_id:
        raise ValueError("Unauthorized")
    
    ref.delete()


def complete_goal(user_id: str, goal_id: str) -> Goal:
    db = get_db()
    ref = db.collection(COLLECTION).document(goal_id)
    
    doc = ref.get()
    if not doc.exists:
        raise ValueError("Goal not found")
    
    data = doc.to_dict()
    if data.get("userId") != user_id:
        raise ValueError("Unauthorized")
    
    ref.update({"status": GoalStatus.completed})
    data["status"] = GoalStatus.completed
    
    return Goal(goalId=goal_id, **data)
