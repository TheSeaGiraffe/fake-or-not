import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import JWT_ALGORITHM, JWT_REFRESH_TOKEN_LENGTH, JWT_SECRET_KEY
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


async def has_valid_access_token(token: str = Depends(oauth2_scheme)):
    user_id = get_access_token_payload(token)
    if user_id is None:
        raise InvalidCredentialsException


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_refresh_token(user: User, db: AsyncSession) -> str:
    token_plaintext = secrets.token_urlsafe(JWT_REFRESH_TOKEN_LENGTH)
    token_hash = hash_token(token_plaintext)

    refresh_token = RefreshToken(hash=token_hash, user=user)
    db.add(refresh_token)
    await db.commit()
    return token_plaintext


# Should probably also check the length of the token to make sure that it's actually a
# refresh token
def validate_token_header(
    token_header: str = Depends(APIKeyHeader(name="Authorization")),
) -> None:
    header_parts = token_header.split()
    if len(header_parts) != 2 or header_parts[0] != "Bearer":
        raise InvalidCredentialsException


async def get_current_user_by_refresh_token(
    token_header: str = Depends(APIKeyHeader(name="Authorization")),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    token = token_header.split()[1]
    token_hash = hash_token(token)
    query = select(RefreshToken).where(
        RefreshToken.hash == token_hash,
        RefreshToken.expiry >= datetime.now(timezone.utc),
    )
    result = await db.execute(query)
    refresh_token: RefreshToken | None = result.scalar_one_or_none()
    if refresh_token is None:
        raise InvalidCredentialsException

    return refresh_token.user


async def delete_refresh_token(token_header: str, db: AsyncSession) -> None:
    token = token_header.split()[1]
    token_hash = hash_token(token)
    query = delete(RefreshToken).where(RefreshToken.hash == token_hash)
    await db.execute(query)
    await db.commit()
