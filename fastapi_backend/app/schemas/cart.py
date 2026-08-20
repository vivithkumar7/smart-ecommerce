from pydantic import BaseModel
from typing import List


class CartAddRequest(BaseModel):

    product_id: int
    quantity: int = 1


class CartUpdateRequest(BaseModel):

    product_id: int
    quantity: int


class CartRemoveRequest(BaseModel):

    product_id: int


class CartItemResponse(BaseModel):

    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    item_total: float


class CartResponse(BaseModel):

    cart_id: int

    items: List[CartItemResponse]

    subtotal: float
    tax: float
    grand_total: float