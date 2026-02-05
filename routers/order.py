# routers/order.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import crud, schemas, database
from routers.utils import get_role, get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])
get_db = database.get_db


# ---------------- PLACE ORDER FROM CART (CUSTOMER) -----------------
@router.post("/", response_model=schemas.OrderResponse)
def place_order(
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    if role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can place orders")

    cart_items = db.query(crud.databasemodels.Cart).filter(
        crud.databasemodels.Cart.user_id == current_user.id
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_data = schemas.OrderCreate(
        items=[
            schemas.OrderItemSchema(product_id=item.product_id, quantity=item.quantity)
            for item in cart_items
        ]
    )

    try:
        order = crud.create_order(db, current_user.id, order_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Clear cart for this user
    for item in cart_items:
        db.delete(item)
    db.commit()

    return schemas.OrderResponse.model_validate(order)


# ---------------- LIST ORDERS (ADMIN OR CUSTOMER) -----------------
@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    if role == "admin":
        orders = crud.get_all_orders(db)
        return [schemas.OrderResponse.model_validate(o) for o in orders]

    if role == "customer":
        # customer can only view their own orders
        target_user_id = current_user.id

        # if they pass user_id and it's different -> block
        if user_id is not None and user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot view another user's orders")

        orders = crud.get_orders_by_user(db, target_user_id)
        return [schemas.OrderResponse.model_validate(o) for o in orders]

    raise HTTPException(status_code=403, detail="Invalid role")


# ---------------- UPDATE ORDER STATUS (ADMIN) -----------------
@router.put("/{order_id}", response_model=schemas.OrderResponse)
def update_order(
    order_id: int,
    status: str = Query(..., description="pending/completed/cancelled"),
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update orders")

    try:
        order = crud.update_order_status(db, order_id, status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return schemas.OrderResponse.model_validate(order)


# ---------------- DELETE ORDER (ADMIN) -----------------
@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete orders")

    order = db.query(crud.databasemodels.Order).filter(crud.databasemodels.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"detail": "Order deleted"}


# ---------------- MAKE PAYMENT (CUSTOMER) -----------------
@router.post("/{order_id}/pay", response_model=schemas.PaymentResponse)
def make_payment(
    order_id: int,
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    if role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can make payments")

    order = db.query(crud.databasemodels.Order).filter(crud.databasemodels.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # customer can only pay for their own order
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot pay for another user's order")

    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order is already paid")

    # Build a fresh PaymentCreate (don't mutate request model)
    payment_data = schemas.PaymentCreate(
        order_id=order_id,
        amount=payment.amount,
        payment_status=payment.payment_status,
        payment_method=payment.payment_method,
    )

    try:
        new_payment = crud.create_payment(db, payment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update order payment_status
    order.payment_status = "paid"
    db.commit()
    db.refresh(order)

    return schemas.PaymentResponse.model_validate(new_payment)
