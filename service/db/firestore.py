from google.cloud import firestore
from typing import Any

_db: Any = None

def get_db() -> Any:
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db
