from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_async_session
from src.auth.schemas import UserAdd, UserLogin, FormUserLogin
from src.auth.service import add_user_to_db, login_user_from_db
from src.auth.utils import get_current_user

auth_router = APIRouter()


@auth_router.post("/reg")
async def reg_user(
        user: UserAdd,
        session: AsyncSession = Depends(get_async_session)
):
    return await add_user_to_db(user, session)


@auth_router.post("/login")
async def login_user(
        form_data: FormUserLogin = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    return await login_user_from_db(form_data.model, session)


@auth_router.get("/me")
async def get_my_posts(user_id: str = Depends(get_current_user)):
    return {"message": f"Posts for user {user_id}"}

