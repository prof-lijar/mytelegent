from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ParsedMessageCommand(BaseModel):
    recipient: str
    message: str
    scheduled_time: datetime

class ScheduledMessage(BaseModel):
    id: Optional[int] = None
    recipient: str
    message: str
    scheduled_time: datetime
    status: str = "pending"
    created_at: datetime = datetime.now()
