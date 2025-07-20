from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.database.connection import get_async_session
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.password import verify_password

InvalidCredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user: User | None = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None
    return user


# Wondering if I shouldn't just hardcode the payload and have it always be the user ID
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)


def get_access_token_payload(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except InvalidTokenError:
        return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token", refreshUrl="/user/refresh")


async def get_current_user_by_access_token(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)
) -> User:
    user_id = get_access_token_payload(token)
    if user_id is None:
        raise InvalidCredentialsException
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user: User | None = result.scalar_one_or_none()
    if user is None:
        raise InvalidCredentialsException
    return user


async def create_refresh_token(user: User, db: AsyncSession) -> RefreshToken:
    refresh_token = RefreshToken(user=user)
    db.add(refresh_token)
    await db.commit()
    return refresh_token


async def get_current_user_by_refresh_token(
    token_header: str = Depends(APIKeyHeader(name="Authorization")),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    header_parts = token_header.split()
    if len(header_parts) != 2 or header_parts[0] != "Bearer":
        raise InvalidCredentialsException

    token = header_parts[1]
    query = select(RefreshToken).where(
        RefreshToken.plaintext == token,
        RefreshToken.expiry >= datetime.now(timezone.utc),
    )
    result = await db.execute(query)
    refresh_token: RefreshToken | None = result.scalar_one_or_none()
    if refresh_token is None:
        raise InvalidCredentialsException

    # query = select(RefreshToken.user).where(RefreshToken.id == refresh_token.id)
    query = select(RefreshToken).where(RefreshToken.id == refresh_token.id)
    result = await db.execute(query)
    # user: User | None = result.scalar_one_or_none()
    # user: User = result.scalar_one()
    refresh_token_from_id: RefreshToken = result.scalar_one()
    return refresh_token_from_id.user
