from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field

class ParsedMessageCommand(BaseModel):
    """Parsed command from natural language input."""
    target: str
    target_type: Literal["name", "username", "phone"]
    scheduled_time: datetime
    message: str
    confidence: float = Field(ge=0.0, le=1.0)

class ScheduledMessage(BaseModel):
    """Message scheduled for delivery."""
    id: Optional[int] = None
    target: str
    target_type: Literal["name", "username", "phone"]
    scheduled_time: datetime
    message: str
    status: Literal["pending", "processing", "sent", "failed", "cancelled"] = "pending"
    retry_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
