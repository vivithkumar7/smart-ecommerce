from pydantic import BaseModel


class OrderStatusUpdateRequest(BaseModel):
    order_status: str
