from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):

    name: str
    description: Optional[str] = None
    category: str
    price: float
    popularity: float = 0
    stock: int = 0
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):

    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True