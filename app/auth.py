import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from .database import SessionLocal
from . import models

# ---=== Load environment variables ===---
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")

# ---=== Setup token login request ===---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ---=== Setup for password encryption ===---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---=== Hash password ===---
def hash_password(password: str) -> str:
    """
    Hashes password for security
    :param password: the plaintext password
    :return: the hashed password
    """
    return pwd_context.hash(password)

# ---=== Verify password ===---
def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifies password against hashed password
    :param plain: the plaintext password
    :param hashed: the hashed password
    :return boolean: True for verified, False for not verified
    """
    return pwd_context.verify(plain, hashed)

# ---=== Create token ===---
def create_access_token(data: dict) -> str:
    """
    Generate and return an access token
    :param data: user data to encode
    :return token: jwt token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(ACCESS_TOKEN_EXPIRES_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    """
    Gives access to the database
    :return db: database object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---=== Current User ===---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current user using the OAuth2 token
    :param token: authentication token
    :param db: database object
    :return user: user object
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user