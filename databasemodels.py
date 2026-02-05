# databasemodels.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Text
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


# -------------------------
# USER MODEL
# -------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20))

    role = Column(String(20), nullable=False, default="customer")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete")
    carts = relationship("Cart", back_populates="user", cascade="all, delete")


# -------------------------
# CATEGORY MODEL
# -------------------------

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete"
    )


# -------------------------
# PRODUCT MODEL
# -------------------------

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    description = Column(Text)

    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    image_url = Column(String(255))

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    category = relationship("Category", back_populates="products")

    carts = relationship("Cart", back_populates="product", cascade="all, delete")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete")


# -------------------------
# CART MODEL
# -------------------------

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)

    # Prevent duplicate cart items
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product"),
    )

    # Relationships
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")


# -------------------------
# ORDER MODEL
# -------------------------

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    order_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    payment_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="orders")

    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete"
    )

    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        cascade="all, delete"
    )


# -------------------------
# ORDER ITEM MODEL
# -------------------------

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


# -------------------------
# PAYMENT MODEL
# -------------------------

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    amount = Column(Float, nullable=False)
    payment_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )
    payment_method = Column(String(50), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    # Relationships
    order = relationship("Order", back_populates="payment")
