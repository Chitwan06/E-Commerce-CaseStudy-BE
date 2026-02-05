# crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

import databasemodels
import schemas

# ---------------- CONSTANTS -----------------
VALID_ROLES = ["admin", "customer"]
VALID_ORDER_STATUSES = ["pending", "completed", "cancelled"]
VALID_PAYMENT_STATUSES = ["pending", "paid", "failed"]


def utcnow():
    return datetime.now(timezone.utc)


# ---------------- USER -----------------
def get_user_by_email(db: Session, email: str):
    return db.query(databasemodels.User).filter(databasemodels.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(databasemodels.User).filter(databasemodels.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    role = (user.role or "customer").strip().lower()
    if role not in VALID_ROLES:
        raise ValueError("Invalid role")

    db_user = databasemodels.User(
        name=user.name,
        email=user.email,
        password=user.password,  # hash in production
        phone=user.phone,
        role=role,
        created_at=utcnow()
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Email already registered")
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: dict):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    # avoid updating immutable fields
    user_data.pop("id", None)
    user_data.pop("created_at", None)

    if "role" in user_data and user_data["role"] is not None:
        role = str(user_data["role"]).strip().lower()
        if role not in VALID_ROLES:
            raise ValueError("Invalid role")
        user_data["role"] = role

    for key, value in user_data.items():
        if hasattr(db_user, key) and value is not None:
            setattr(db_user, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Update failed (possible duplicate email)")
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return True


# ---------------- CATEGORY -----------------
def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = databasemodels.Category(
        name=category.name,
        description=category.description,
        created_at=utcnow()
    )
    db.add(db_category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Category name already exists")
    db.refresh(db_category)
    return db_category


def get_categories(db: Session):
    return db.query(databasemodels.Category).all()


def get_category_by_id(db: Session, category_id: int):
    return db.query(databasemodels.Category).filter(databasemodels.Category.id == category_id).first()


def update_category(db: Session, category_id: int, category_data: dict):
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        return None

    category_data.pop("id", None)
    category_data.pop("created_at", None)

    for key, value in category_data.items():
        if hasattr(db_category, key) and value is not None:
            setattr(db_category, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Category name already exists")
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        return None
    db.delete(db_category)
    db.commit()
    return True


# ---------------- PRODUCT -----------------
def create_product(db: Session, product: schemas.ProductCreate):
    category = get_category_by_id(db, product.category_id)
    if not category:
        raise ValueError("Category not found")

    if product.price <= 0:
        raise ValueError("Invalid price")
    if product.stock < 0:
        raise ValueError("Invalid stock")

    db_product = databasemodels.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id,
        image_url=product.image_url,
        created_at=utcnow()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session):
    return db.query(databasemodels.Product).all()


def get_product_by_id(db: Session, product_id: int):
    return db.query(databasemodels.Product).filter(databasemodels.Product.id == product_id).first()


# Your original name said "subcategory" but logic is category_id. Keep it but correct meaning.
def get_products_by_category_id(db: Session, category_id: int):
    return db.query(databasemodels.Product).filter(databasemodels.Product.category_id == category_id).all()


def get_products_by_category(db: Session, category_id: int):
    # no join needed, but keeping style is fine
    return db.query(databasemodels.Product).filter(databasemodels.Product.category_id == category_id).all()


def update_product(db: Session, product_id: int, product_data: dict):
    db_product = get_product_by_id(db, product_id)
    if not db_product:
        return None

    product_data.pop("id", None)
    product_data.pop("created_at", None)

    if "category_id" in product_data and product_data["category_id"] is not None:
        cat = get_category_by_id(db, int(product_data["category_id"]))
        if not cat:
            raise ValueError("Category not found")

    if "price" in product_data and product_data["price"] is not None:
        if float(product_data["price"]) <= 0:
            raise ValueError("Invalid price")

    if "stock" in product_data and product_data["stock"] is not None:
        if int(product_data["stock"]) < 0:
            raise ValueError("Invalid stock")

    for key, value in product_data.items():
        if hasattr(db_product, key) and value is not None:
            setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product_by_id(db, product_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
    return True


# ---------------- CART -----------------
def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    # optional: validate user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    product = get_product_by_id(db, product_id)
    if not product:
        raise ValueError("Product not found")

    if quantity <= 0:
        raise ValueError("Invalid quantity")

    # if already exists, increase quantity (because you have UniqueConstraint)
    existing = db.query(databasemodels.Cart).filter(
        databasemodels.Cart.user_id == user_id,
        databasemodels.Cart.product_id == product_id
    ).first()

    if existing:
        new_qty = existing.quantity + quantity
        if new_qty > product.stock:
            raise ValueError("Quantity exceeds available stock")
        existing.quantity = new_qty
        db.commit()
        db.refresh(existing)
        return existing

    if quantity > product.stock:
        raise ValueError("Quantity exceeds available stock")

    db_cart = databasemodels.Cart(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity
    )
    db.add(db_cart)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("This product is already in cart")
    db.refresh(db_cart)
    return db_cart


def get_cart_by_user(db: Session, user_id: int):
    return db.query(databasemodels.Cart).filter(databasemodels.Cart.user_id == user_id).all()


def remove_from_cart(db: Session, cart_id: int):
    cart_item = db.query(databasemodels.Cart).filter(databasemodels.Cart.id == cart_id).first()
    if not cart_item:
        return None
    db.delete(cart_item)
    db.commit()
    return True


# ---------------- ORDER -----------------
def create_order(db: Session, user_id: int, order_data: schemas.OrderCreate):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    if not order_data.items:
        raise ValueError("Order must contain at least one item")

    new_order = databasemodels.Order(
        user_id=user_id,
        order_status="pending",
        payment_status="pending",
        created_at=utcnow()
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    try:
        # Add order items + deduct stock
        for item in order_data.items:
            product = get_product_by_id(db, item.product_id)
            if not product:
                raise ValueError(f"Product {item.product_id} not found")

            if item.quantity <= 0:
                raise ValueError("Invalid quantity")

            if item.quantity > product.stock:
                raise ValueError(f"Not enough stock for product {product.name}")

            product.stock -= item.quantity
            db_item = databasemodels.OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(db_item)

        db.commit()
    except Exception:
        db.rollback()
        # cleanup created order if items failed
        try:
            db.delete(new_order)
            db.commit()
        except Exception:
            db.rollback()
        raise

    db.refresh(new_order)
    return new_order


def get_orders_by_user(db: Session, user_id: int):
    return db.query(databasemodels.Order).filter(databasemodels.Order.user_id == user_id).all()


def get_all_orders(db: Session):
    return db.query(databasemodels.Order).all()


def update_order_status(db: Session, order_id: int, status: str):
    status = status.strip().lower()
    if status not in VALID_ORDER_STATUSES:
        raise ValueError(f"Invalid order status: {status}")

    order = db.query(databasemodels.Order).filter(databasemodels.Order.id == order_id).first()
    if not order:
        return None

    order.order_status = status
    db.commit()
    db.refresh(order)
    return order


# ---------------- PAYMENT -----------------
def create_payment(db: Session, payment: schemas.PaymentCreate):
    # ensure order exists
    order = db.query(databasemodels.Order).filter(databasemodels.Order.id == payment.order_id).first()
    if not order:
        raise ValueError("Order not found")

    # ensure only one payment per order (Payment.order_id unique recommended in model)
    existing = db.query(databasemodels.Payment).filter(databasemodels.Payment.order_id == payment.order_id).first()
    if existing:
        raise ValueError("Payment already exists for this order")

    status = str(payment.payment_status).strip().lower()
    if status not in VALID_PAYMENT_STATUSES:
        raise ValueError("Invalid payment status")

    if payment.amount <= 0:
        raise ValueError("Invalid amount")

    db_payment = databasemodels.Payment(
        order_id=payment.order_id,
        amount=payment.amount,
        payment_status=status,
        payment_method=payment.payment_method,
        created_at=utcnow()
    )
    db.add(db_payment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Payment creation failed")
    db.refresh(db_payment)
    return db_payment


def get_payments(db: Session):
    return db.query(databasemodels.Payment).all()


def update_payment_status(db: Session, payment_id: int, status: str):
    status = status.strip().lower()
    if status not in VALID_PAYMENT_STATUSES:
        raise ValueError(f"Invalid payment status: {status}")

    payment = db.query(databasemodels.Payment).filter(databasemodels.Payment.id == payment_id).first()
    if not payment:
        return None

    payment.payment_status = status
    db.commit()
    db.refresh(payment)
    return payment
