from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas, database
from routers.utils import get_role

router = APIRouter(prefix="/categories", tags=["Categories"])
get_db = database.get_db

# ----- ADMIN: Add Category -----
@router.post("/", response_model=schemas.CategoryResponse)
def add_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add categories")
    return crud.create_category(db, category)

# ----- LIST ALL CATEGORIES: Admin + Customer -----
@router.get("/", response_model=List[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

# ----- ADMIN: Update Category -----
@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update categories")
    db_category = db.query(crud.databasemodels.Category).filter(crud.databasemodels.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

# ----- ADMIN: Delete Category -----
@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete categories")
    db_category = db.query(crud.databasemodels.Category).filter(crud.databasemodels.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"detail": "Category deleted"}
