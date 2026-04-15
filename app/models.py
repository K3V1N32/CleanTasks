from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
"""
Database models for SQLAlchemy are defined here, so far there is just users and tasks tables
"""


# ---=== USER ===---
class User(Base):
    """
    User database model
    variables: id: int, username: str, password: str
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    tasks = relationship("Task", back_populates="owner", cascade="all, delete")

# ---=== TASK ===---
class Task(Base):
    """
    Task database model inherits owner_id from user
    variables: id: int, title: str, description: str, owner_id: int
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    position = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    ai_generated = Column(Boolean, default=False)
    ai_summary = Column(String, nullable=True)
    ai_breakdown = Column(String, nullable=True)

    owner = relationship("User")