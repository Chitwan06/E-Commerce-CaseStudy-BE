# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta,timezone
from jose import jwt
from passlib.context import CryptContext

import crud, schemas, database

router = APIRouter(prefix="/auth", tags=["Auth"])
get_db = database.get_db

# ----------------- Config -----------------
SECRET_KEY = "your_super_secret_key_here"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------- Utils -----------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ----------------- Register -----------------
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # hash password
    hashed_password = get_password_hash(user.password)

    # IMPORTANT: create user without mutating Pydantic object unexpectedly
    user_data = schemas.UserCreate(
        name=user.name,
        email=user.email,
        password=hashed_password,
        phone=user.phone,
        role=user.role or "customer",
    )

    new_user = crud.create_user(db, user_data)

    # Pydantic v2 style
    return schemas.UserResponse.model_validate(new_user)


# ----------------- Login -----------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2PasswordRequestForm uses:
      - username (we use email here)
      - password
    """
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
