from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_async_session
from src.auth.schemas import UserAdd
from src.auth.service import add_user_to_db

auth_router = APIRouter()


@auth_router.post("/reg")
async def reg_user(
        user: UserAdd,
        session: AsyncSession = Depends(get_async_session)
):
    return await add_user_to_db(user, session)

