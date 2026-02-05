from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import crud, schemas, database
from routers.utils import get_role

router = APIRouter(prefix="/products", tags=["Products"])
get_db = database.get_db


# ----------------------
# CREATE PRODUCT (ADMIN)
# ----------------------
@router.post("/", response_model=schemas.ProductResponse)
def add_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add products")

    try:
        return crud.create_product(db, product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------
# LIST PRODUCTS (ADMIN + CUSTOMER)
# Optional filtering by category_id or name
# ----------------------
@router.get("/", response_model=List[schemas.ProductResponse])
def list_products(
    category_id: Optional[int] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(crud.databasemodels.Product)

    if name:
        query = query.filter(crud.databasemodels.Product.name.ilike(f"%{name}%"))

    if category_id:
        query = query.filter(crud.databasemodels.Product.category_id == category_id)

    return query.all()


# ----------------------
# GET PRODUCT BY ID (ADMIN + CUSTOMER)
# ----------------------
@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ----------------------
# UPDATE PRODUCT (ADMIN)
# ----------------------
@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update products")

    db_product = crud.get_product_by_id(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        updated = crud.update_product(db, product_id, product.model_dump())
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------
# DELETE PRODUCT (ADMIN)
# ----------------------
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(get_role),
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete products")

    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"detail": "Product deleted"}
