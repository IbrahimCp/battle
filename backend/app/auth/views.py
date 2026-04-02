from fastapi import APIRouter, HTTPException, Depends, status

from app.database.core import DbSession
from app.auth.models import(
    UserRegister,
    UserPublic,
    RefreshTokenRequest
)
from app.auth.service import (
    create,
    get_by_username,
    get_by_email,
    create_access_token,
    create_refresh_token,
    verify_jwt,
    get_current_user
)

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"], prefix="/auth")

@router.get("/me", response_model=UserPublic)
def get_me(
    current_user: UserPublic = Depends(get_current_user)
):
    return current_user


@router.post("/login")
def login(
    db_session: DbSession,
    form_data: OAuth2PasswordRequestForm = Depends()
):  
    user = get_by_username(db_session=db_session, username=form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(user_id=user.id, username=user.username)
    refresh_token = create_refresh_token(user_id=user.id, username=user.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token(
    refresh_in: RefreshTokenRequest,
    db_session: DbSession,
):
    """
    Refresh access token using a refresh token.
    """
    payload = verify_jwt(refresh_in.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    username = payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = get_by_username(db_session=db_session, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    access_token = create_access_token(user_id=user.id, username=user.username)
    new_refresh_token = create_refresh_token(user_id=user.id, username=user.username)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserPublic)
def register(
    user_in: UserRegister, 
    db_session: DbSession
): 
    if get_by_username(db_session=db_session, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "A user with this username already exists.",
                    "loc": ["username"],
                    "type": "value_error",
                }
            ],
        )

    if get_by_email(db_session=db_session, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "A user with this email already exists.",
                    "loc": ["email"],
                    "type": "value_error",
                }
            ],
        )

    user = create(db_session=db_session, user_in=user_in)
    return user


@router.post("/logout")
def logout(
    current_user=Depends(get_current_user),
):
    return {"message": "Successfully logged out"}
