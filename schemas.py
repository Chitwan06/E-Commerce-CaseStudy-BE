# schemas.py
from __future__ import annotations

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum
from typing_extensions import Literal


# ---------------- ROLE ENUM -----------------
class RoleEnum(str, Enum):
    admin = "admin"
    customer = "customer"


# ---------------- USER SCHEMAS -----------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: Optional[str] = "customer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is None:
            return "customer"
        v = str(v).strip().lower()
        if v not in ["admin", "customer"]:
            raise ValueError("Invalid role")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserWithOrdersResponse(UserResponse):
    orders: Optional[List["OrderResponse"]] = None


# ---------------- CATEGORY SCHEMAS -----------------
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------- PRODUCT SCHEMAS -----------------
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: int
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None  

    model_config = {"from_attributes": True}


# ---------------- CART SCHEMAS -----------------
class CartBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class CartCreate(CartBase):
    pass


class CartResponse(CartBase):
    id: int
    product: Optional[ProductResponse] = None  # nested product info (relationship)

    model_config = {"from_attributes": True}


# ---------------- ORDER SCHEMAS -----------------
class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemSchema]


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    product: Optional[ProductResponse] = None

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_status: str
    payment_status: str
    created_at: datetime
    order_items: Optional[List[OrderItemResponse]] = None  

    model_config = {"from_attributes": True}


# ---------------- PAYMENT SCHEMAS -----------------
class PaymentBase(BaseModel):
    order_id: int
    amount: float
    payment_status: Literal["pending", "paid", "failed"]
    payment_method: str


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime
    order: Optional[OrderResponse] = None

    model_config = {"from_attributes": True}


# ---------------- Forward references -----------------
UserWithOrdersResponse.model_rebuild()
ProductResponse.model_rebuild()
CartResponse.model_rebuild()
OrderResponse.model_rebuild()
OrderItemResponse.model_rebuild()
PaymentResponse.model_rebuild()
