from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="")
    price: float = Field(..., ge=0)
    image: Optional[str] = None
    category: Optional[str] = None
    in_stock: bool = True


class ProductOut(Product):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)


class Cart(BaseModel):
    session_id: str
    items: List[CartItem]


class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)
    price_each: float = Field(..., ge=0)


class Order(BaseModel):
    session_id: str
    items: List[OrderItem]
    total: float = Field(..., ge=0)
    status: str = "pending"


class OrderOut(Order):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
