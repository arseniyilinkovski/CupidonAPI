from datetime import datetime, timedelta

from select import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserAdd, UserLogin
from src.auth.utils import hash_password, create_access_token, verify_password
from src.config import settings
from src.database.models import Users, RefreshTokens

from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


async def add_user_to_db(user_data: UserAdd, session: AsyncSession):
    existing_user = await session.scalar(
        select(Users).where(Users.email == user_data.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    user_data.password = hash_password(user_data.password)

    user = Users(**user_data.dict())

    access_token = create_access_token({"sub": user.email})

    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении пользователя"
        )

    return {
        "JWT-токен": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }


async def login_user_from_db(user_data: UserLogin, session: AsyncSession):
    user = await session.scalar(select(Users).where(Users.email == user_data.email))
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибочные данные!"
        )
    access_token = create_access_token({"sub": user.email})
    refresh_token = RefreshTokens(
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=settings.get_refresh_token_expire_days())
    )
    session.add(refresh_token)
    await session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer"
    }


async def refresh_access_token_in_db(token: str, session: AsyncSession):
    token = await session.scalar(
        select(RefreshTokens).where(RefreshTokens.token == token)
    )
    if not token or token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Недействительный или истекший refresh токен")

    user = await session.scalar(
        select(Users).where(Users.id == token.user_id)
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользотватель не найден")

    new_access_token = create_access_token({"sub": user.email})
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


async def logout_user_from_db(token: str, session: AsyncSession):
    result = await session.execute(
        select(RefreshTokens).where(RefreshTokens.token == token)
    )

    token = result.scalar_one_or_none()
    if token:
        await session.delete(token)
        await session.commit()
    return {
        "detail": "Вы вышли из системы"
    }





