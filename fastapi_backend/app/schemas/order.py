from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    quantity: int
    unit_price: float


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str
    timestamp: datetime


class CheckoutResponse(BaseModel):
    order_id: int
    amount: float
    currency: str
    payment_intent_id: str
    checkout_session_id: str
    checkout_url: Optional[str] = None
    payment_status: str
    order_status: str


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total: float
    payment_status: str
    order_status: str
    created_at: datetime
    items: List[OrderItemResponse]
    payments: List[PaymentResponse]
