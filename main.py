# main.py
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import database
import databasemodels
import schemas
from routers import users, product, category, cart, order, auth

app = FastAPI(title="Ecommerce Backend")

database.init_db()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(product.router)
app.include_router(category.router)
app.include_router(cart.router)
app.include_router(order.router)

@app.get("/")
def root():
    return {"message": "Welcome to Ecommerce API! Visit /docs for API documentation."}


# -------------------- Product Search (no SubCategory) --------------------
get_db = database.get_db

@app.get("/products/search", response_model=List[schemas.ProductResponse])
def search_products(
    name: Optional[str] = Query(None, description="Search by product name"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(databasemodels.Product)

    if name:
        query = query.filter(databasemodels.Product.name.ilike(f"%{name}%"))

    if category_id:
        query = query.filter(databasemodels.Product.category_id == category_id)

    return query.offset(skip).limit(limit).all()
