from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_async_session
from src.auth.service import get_current_user, require_scope
from src.profiles.schemas import FormProfileCreate, FormProfileUpdate
from src.profiles.service import get_user_profile_from_db, \
    get_profiles_from_db, handle_add_profile, change_user_profile_in_db, like_user_profile_in_db, get_next_profile, \
    dislike_user_profile_in_db

profiles_router = APIRouter()


@profiles_router.post("/add_profile")
async def add_user_profile(
    request: Request,
    form: FormProfileCreate = Depends(),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),

):
    return await handle_add_profile(form, user, session, request)


@profiles_router.get("/get_profile")
async def get_user_profile(
        user=Depends(require_scope("profile:read")),
        session: AsyncSession = Depends(get_async_session)
):
    return await get_user_profile_from_db(user.id, session)


@profiles_router.get("/get_profiles")
async def get_profiles(
        user=Depends(require_scope("admin")),
        session: AsyncSession = Depends(get_async_session)
):
    return await get_profiles_from_db(user, session)


@profiles_router.patch("/change_profile")
async def change_profile(
        request: Request,
        form: FormProfileUpdate = Depends(),
        session: AsyncSession = Depends(get_async_session),
        user=Depends(require_scope("profile:edit")),

):
    return await change_user_profile_in_db(form, session, user, request)


@profiles_router.post("/like")
async def like_user_profile(
        liked_user_id: int,
        session: AsyncSession = Depends(get_async_session),
        user=Depends(require_scope("profile:like"))
):
    return await like_user_profile_in_db(liked_user_id, session, user)


@profiles_router.get("/next_profile")
async def next_profile_handle(
        user=Depends(require_scope("profile:view")),
        session: AsyncSession = Depends(get_async_session),
):
    return await get_next_profile(user, session)


@profiles_router.post("/dislike")
async def dislike_user_profile(
        disliked_user_id: int,
        user=Depends(require_scope("profile:dislike")),
        session: AsyncSession = Depends(get_async_session)
):
    return await dislike_user_profile_in_db(disliked_user_id, session, user)

