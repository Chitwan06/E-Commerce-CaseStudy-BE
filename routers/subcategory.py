# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# import crud, schemas, database
# from routers.utils import get_role

# router = APIRouter(prefix="/subcategories", tags=["SubCategories"])
# get_db = database.get_db

# # ----- ADMIN: Add SubCategory -----
# @router.post("/", response_model=schemas.SubCategoryResponse)
# def add_subcategory(subcat: schemas.SubCategoryCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
#     if role != "admin":
#         raise HTTPException(status_code=403, detail="Only admin can add subcategories")
#     return crud.create_subcategory(db, subcat)  # You need to implement this in crud.py

# # ----- LIST ALL SubCategories -----
# @router.get("/", response_model=List[schemas.SubCategoryResponse])
# def list_subcategories(db: Session = Depends(get_db)):
#     return crud.get_subcategories(db)  # Implement in crud.py

# # ----- ADMIN: Update SubCategory -----
# @router.put("/{subcat_id}", response_model=schemas.SubCategoryResponse)
# def update_subcategory(subcat_id: int, subcat: schemas.SubCategoryCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
#     if role != "admin":
#         raise HTTPException(status_code=403, detail="Only admin can update subcategories")
#     db_subcat = db.query(crud.databasemodels.SubCategory).filter(crud.databasemodels.SubCategory.id == subcat_id).first()
#     if not db_subcat:
#         raise HTTPException(status_code=404, detail="SubCategory not found")
#     for key, value in subcat.dict().items():
#         setattr(db_subcat, key, value)
#     db.commit()
#     db.refresh(db_subcat)
#     return db_subcat

# # ----- ADMIN: Delete SubCategory -----
# @router.delete("/{subcat_id}")
# def delete_subcategory(subcat_id: int, db: Session = Depends(get_db), role: str = Depends(get_role)):
#     if role != "admin":
#         raise HTTPException(status_code=403, detail="Only admin can delete subcategories")
#     db_subcat = db.query(crud.databasemodels.SubCategory).filter(crud.databasemodels.SubCategory.id == subcat_id).first()
#     if not db_subcat:
#         raise HTTPException(status_code=404, detail="SubCategory not found")
#     db.delete(db_subcat)
#     db.commit()
#     return {"detail": "SubCategory deleted"}
