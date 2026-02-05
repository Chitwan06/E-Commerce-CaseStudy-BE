# routers/cart.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

import crud, schemas, database
import databasemodels
from routers.utils import get_role, get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])
get_db = database.get_db


@router.post("/", response_model=schemas.CartResponse)
def add_to_cart(
    cart_item: schemas.CartCreate,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    if role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can add to cart")

    if cart_item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot add items to another user's cart")

    try:
        return crud.add_to_cart(
            db=db,
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[schemas.CartResponse])
def get_cart(
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    if role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can view their cart")

    return crud.get_cart_by_user(db, current_user.id)


@router.put("/{cart_id}", response_model=schemas.CartResponse)
def update_cart_quantity(
    cart_id: int,
    quantity: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    if role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can update cart")

    cart_item = db.query(databasemodels.Cart).filter(databasemodels.Cart.id == cart_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if cart_item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another user's cart item")

    try:
        return crud.update_cart_quantity(db, cart_id, quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}")
def remove_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
    current_user: schemas.UserResponse = Depends(get_current_user),
):
    if role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can remove items from cart")

    cart_item = db.query(databasemodels.Cart).filter(databasemodels.Cart.id == cart_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if cart_item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot remove another user's cart item")

    removed = crud.remove_from_cart(db, cart_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"detail": "Item removed from cart"}
