from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory or root directory
backend_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_threatlens.db")

# Render uses postgres:// in env vars, but SQLAlchemy 1.4+ requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()