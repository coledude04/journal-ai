import os
from google.cloud import firestore
from typing import Any

_db: Any = None
ENV = os.getenv("ENV", "dev")

def get_db() -> Any:
    global _db
    if _db is None:
        _db = firestore.Client(database=get_db_name())
    return _db

def get_db_name() -> str:
    if ENV == "prod":
        return "ai-journal-prod"
    else:
        return "ai-journal-dev"
