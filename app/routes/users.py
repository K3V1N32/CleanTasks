from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..auth import hash_password, verify_password, create_access_token, get_current_user

# ---=== Initialize Router ===---
router = APIRouter()

def get_db():
    """
    Gives access to the database
    :return db: database object
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---=== CREATE USER ===---
@router.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user, checking for username to make sure usernames are unique
    :param user:
    :param db:
    :return: user object that has been created
    """
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = models.User(username=user.username, password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ---=== LOGIN ===---
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Securely log user into the api
    :param form_data:
    :param db:
    :return: access token
    """
    db_user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": db_user.id})

    return {"access_token": token, "token_type": "bearer"}

# ---=== VALIDATION ===---
@router.get("/users/me")
def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Used for validating user tokens
    :param current_user:
    :return: id/username on success, 401 error on failure
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
    }