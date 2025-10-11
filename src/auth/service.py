from datetime import datetime, timedelta

from jose import jwt, JWTError
from pydantic_core import ValidationError
from select import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.auth.dependencies import oauth2_scheme, get_async_session
from src.auth.schemas import UserAdd, UserLogin
from src.auth.utils import hash_password, create_access_token, verify_password, create_confirmation_token, \
    send_confirmation_email, SECRET_KEY, ALGORITHM
from src.config import settings
from src.database.models import Users, RefreshTokens

from sqlalchemy import select
from fastapi import HTTPException, status, Depends
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
    email_confirmation_token = create_confirmation_token()
    user.confirmation_token = email_confirmation_token
    await send_confirmation_email(
        user.email,
        email_confirmation_token,
        "Подтверждение email",
        "Для подтверждения email, пожалуйста, перейдите по ссылке:",
        "/auth/confirm"
    )
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
    try:

        user = await session.scalar(select(Users).where(Users.email == user_data.email))
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибочные данные!"
            )
        access_token = create_access_token({"sub": user.email})
        existing_refresh_tokens = await session.scalars(
            select(RefreshTokens).where(RefreshTokens.user_id == user.id)
        )
        refresh_tokens_list = list(existing_refresh_tokens)
        if len(refresh_tokens_list) > 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Превышено время одновременных сессий!"
            )
        refresh_token = RefreshTokens(
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=settings.get_refresh_token_expire_days())
        )
        session.add(refresh_token)
        await session.commit()

        response = JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer"
            }
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token.token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=60 * 60 * 24 * settings.get_refresh_token_expire_days()
        )
        return response
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Введены неверные данные"
        )


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
    await session.delete(token)

    new_refresh_token = RefreshTokens(
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=settings.get_refresh_token_expire_days())
    )
    session.add(new_refresh_token)
    await session.commit()

    new_access_token = create_access_token({"sub": user.email})

    response = JSONResponse(content={
        "access_token": new_access_token,
        "token_type": "bearer"
    })
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token.token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * settings.get_refresh_token_expire_days()
    )
    return response


async def logout_user_from_db(token: str, session: AsyncSession):
    result = await session.execute(
        select(RefreshTokens).where(RefreshTokens.token == token)
    )

    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=401, detail="Refresh токен отсутсвует")
    if token:
        await session.delete(token)
        await session.commit()
        response = JSONResponse(content={
            "detail": "Вы вышли из системы"
        })
        response.delete_cookie("refresh_token")
        return response


async def confirm_user_email(token: str, session: AsyncSession):
    user = await session.scalar(select(Users).where(Users.confirmation_token == token))
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Неверный токен"
        )
    user.is_confirmed = True
    user.confirmation_token = None
    await session.commit()
    return {
        "message": "Email успешно подтвержден!"
    }


async def get_current_user(session: AsyncSession = Depends(get_async_session),
                           token: str = Depends(oauth2_scheme),
                           ):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await session.scalar(select(Users).where(Users.email == user_id))
        if not user or not user.is_confirmed:
            raise HTTPException(status_code=403, detail="Email не подтвержден")

        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")


