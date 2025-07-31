from fastapi import HTTPException, status
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schema.user import UserCreate

from .password import get_password_hash


async def create_user(user: UserCreate, db: AsyncSession) -> User:
    hashed_password = get_password_hash(user.password)

    db_user = User(
        **user.model_dump(exclude={"password"}),
        password_hash=hashed_password,
    )

    try:
        db.add(db_user)
        await db.commit()
    except exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    return db_user
