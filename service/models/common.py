from datetime import datetime
from pydantic import BaseModel

class TimestampedModel(BaseModel):
    createdAt: datetime
    updatedAt: datetime | None = None
