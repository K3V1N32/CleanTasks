from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
"""
Database setup and session initialization
"""
# ---=== Load environment variables ===---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ---=== Initialize the SQLAlchemy database engine ===---
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# ---=== SQL Sessions ===---
SessionLocal = sessionmaker(bind=engine)

# ---=== Database setup ===---
Base = declarative_base()