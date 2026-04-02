import time
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.database.core import DbSession

from app.config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_ACCESS_EXPIRY_SECONDS,
    JWT_REFRESH_EXPIRY_SECONDS,
)
from app.auth.models import UserRegister, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(user_id: int, username: str) -> str:
    """Create a JWT token containing user data."""
    payload = {
        "user_id": user_id,
        "username": username,
        "type": "access",
        "exp": int(time.time()) + (JWT_ACCESS_EXPIRY_SECONDS),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: int, username: str) -> str:
    """Create a JWT token containing user data."""
    payload = {
        "user_id": user_id,
        "username": username,
        "type": "refresh",
        "exp": int(time.time()) + (JWT_REFRESH_EXPIRY_SECONDS),
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> dict:
    """Verify and decode a JWT token. Raises on invalid/expired."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )


async def get_current_user(
    db_session: DbSession,
    token: str = Depends(oauth2_scheme),
) -> User:
    """Dependency: extracts and verifies JWT from Authorization header and returns user."""
    payload = verify_jwt(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    username = payload.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing username",
        )
        
    user = get_by_username(db_session=db_session, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def get_by_username(
    db_session: DbSession,
    username: str
):
    return db_session.query(User).filter(User.username == username).first()


def get_by_email(
    db_session: DbSession,
    email: str
):
    return db_session.query(User).filter(User.email == email).first()


def create(
    db_session: DbSession,
    user_in: UserRegister
):
    user = User(
        username=user_in.username,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    user.set_password(user_in.password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
