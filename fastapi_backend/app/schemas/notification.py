from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    message: str
    read_status: bool
    timestamp: datetime
    order_id: int | None = None


class MarkNotificationsReadRequest(BaseModel):
    notification_ids: list[int] | None = None
