from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_async_session
from src.auth.service import get_current_user, require_scope
from src.profiles.schemas import AddProfile
from src.profiles.service import add_user_profile_to_db, validate_user_geo, get_user_profile_from_db, \
    get_profiles_from_db

profiles_router = APIRouter()


@profiles_router.post("/add_profile")
async def add_user_profile(
        data: AddProfile,
        user=Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
        ):
    try:
        await validate_user_geo(data, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return await add_user_profile_to_db(data, session, user["user"].id)


@profiles_router.get("/get_profile")
async def get_user_profile(
        user=Depends(require_scope("profile:read")),
        session: AsyncSession = Depends(get_async_session)
):
    return await get_user_profile_from_db(user.id, session)


@profiles_router.get("/get_profiles")
async def get_profiles(
        user=Depends(require_scope("user:read")),
        session: AsyncSession = Depends(get_async_session)
):
    return await get_profiles_from_db(user, session)

