import re
from pydantic import BaseModel, field_validator

"""
Schemas define the structure and validation of data for the API.

Classes:
UserCreate:
    Schema for creating a new user.
    Attributes:
        username (str): The user's username.
        password (str): The user's password.

TaskCreate:
    Schema for creating a new task.
    Attributes:
        title (str): The title of the task.
        description (str): The task description.

TaskResponse:
    Schema for returning task data to the client.
    Attributes:
        id (int): Unique task identifier.
        title (str): The title of the task.
        description (str): The task description.
        owner_id (int): ID of the user who owns the task.
        ai_generated (bool): Whether or not the task AI parts are generated.
        ai_summary (str): The task AI summary.
        ai_breakdown (str): The task AI breakdown.

"""

class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")

        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password too long (max 72 bytes)")

        return value

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int
    position: int
    completed: bool
    ai_generated: bool
    ai_summary: str | None
    ai_breakdown: str | None

    class Config:
        from_attributes = True