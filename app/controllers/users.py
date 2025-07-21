from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from app.database.connection import get_async_session
from app.models.user import User
from app.schema.token import Token, TokenAccess
from app.schema.user import UserCreate, UserOut
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user_by_access_token,
    get_current_user_by_refresh_token,
)
from app.services.user import create_user

router = APIRouter(prefix="/user")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register_user(
    user: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    db_user = await create_user(user, db)

    return db_user


@router.post("/token")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    email = form_data.username
    password = form_data.password
    user = await authenticate_user(email, password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": f"{user.id}"}, expires_delta=access_token_expires
    )
    token = await create_refresh_token(user, db)

    return Token(access_token=access_token, refresh_token=token)


@router.post("/refresh")
async def refresh_access_token(
    user: User = Depends(get_current_user_by_refresh_token),
):
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": f"{user.id}"}, expires_delta=access_token_expires
    )
    return TokenAccess(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def protected_route(user: User = Depends(get_current_user_by_access_token)):
    return user
