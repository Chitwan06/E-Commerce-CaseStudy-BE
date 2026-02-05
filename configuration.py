# configuration.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ---------------- LOAD ENV ----------------
load_dotenv()


# ---------------- ENV VARS ----------------
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


# ---------------- VALIDATION ----------------
required_vars = {
    "DB_USERNAME": DB_USERNAME,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
}

missing = [k for k, v in required_vars.items() if not v]

if missing:
    raise ValueError(f"Missing environment variables: {', '.join(missing)}")


# ---------------- DATABASE URL ----------------
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USERNAME}:"
    f"{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ---------------- ENGINE ----------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   
    pool_size=5,
    max_overflow=10,
    echo=False,           
    future=True           
)


# ---------------- SESSION ----------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
