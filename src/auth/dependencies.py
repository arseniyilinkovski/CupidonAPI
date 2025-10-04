from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


