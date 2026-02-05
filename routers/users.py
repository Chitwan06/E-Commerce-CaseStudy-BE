from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas, database
from routers.utils import get_role

router = APIRouter(prefix="/users", tags=["Users"])
get_db = database.get_db

@router.post("/", response_model=schemas.UserResponse)
def add_user(user: schemas.UserCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add users")
    return crud.create_user(db, user)

@router.get("/", response_model=List[schemas.UserResponse])
def list_users(db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add users")
    return db.query(crud.databasemodels.User).all()

@router.put("/{user_id}")
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update users")
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete users")
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}
