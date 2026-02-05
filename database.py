# database.py
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from configuration import engine  # make sure engine is defined in configuration.py

# Base class for ORM models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize all tables (call after importing all models)
def init_db():
    Base.metadata.create_all(bind=engine)
