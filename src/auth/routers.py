from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request

from src.auth.dependencies import get_async_session
from src.auth.schemas import UserAdd, UserLogin, FormUserLogin
from src.auth.service import add_user_to_db, login_user_from_db, refresh_access_token_in_db, logout_user_from_db, \
    confirm_user_email
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
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    user_data = UserLogin(email=form_data.username, password=form_data.password)

    return await login_user_from_db(user_data, session)


@auth_router.post("/refresh")
async def refresh_access_token(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    token = request.cookies.get("refresh_token")
    return await refresh_access_token_in_db(token, session)


@auth_router.post("/logout")
async def logout_user(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    token = request.cookies.get("refresh_token")
    return await logout_user_from_db(token, session)


@auth_router.get("/me")
async def get_my_posts(user_id: str = Depends(get_current_user)):
    return {"message": f"Posts for user {user_id}"}


@auth_router.get("/confirm")
async def confirm_email(
        token: str,
        session: AsyncSession = Depends(get_async_session)
):
    return await confirm_user_email(token, session)



