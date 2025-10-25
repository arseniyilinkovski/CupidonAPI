from datetime import datetime

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.models import Profiles, Country, Region, City
from src.profiles.dependencies import get_nsfw_model
from src.profiles.schemas import AddProfile, FormProfileCreate
from src.profiles.utils import upload_photo_to_cloudinary, delete_photo_from_cloudinary
from src.scopes.service import assign_scopes_to_user


async def add_user_profile_to_db(data: AddProfile, session: AsyncSession, user_id: int, photo: dict):
    profile = await session.scalar(
        select(Profiles).where(Profiles.user_id == user_id)
    )
    if profile:
        raise HTTPException(
            status_code=409,
            detail="Профиль для этого пользователя уже существует"
        )

    new_profile = Profiles(
        user_id=user_id,
        name=data.name,
        gender=data.gender,
        orientation=data.orientation,
        birthday=data.birthday,
        last_active_at=datetime.utcnow(),
        country=data.country,
        region=data.region,
        city=data.city,
        bio=data.bio,
        photo_url=photo["photo_url"],
        photo_public_id=photo["photo_public_id"]
    )
    session.add(new_profile)
    await assign_scopes_to_user(session, ['profile:edit'], user_id)
    await session.commit()
    return {
        "message": "Профиль успешно создан",
        "age": new_profile.age,
        "photo_url": new_profile.photo_url
    }


async def handle_add_profile(
    form: FormProfileCreate,
    user,
    session: AsyncSession,
    request: Request
):
    data = form.model

    # 1. Валидация гео-данных
    try:
        await validate_user_geo(data, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Проверка на существующий профиль
    existing_profile = await session.scalar(
        select(Profiles).where(Profiles.user_id == user["user"].id)
    )
    if existing_profile:
        raise HTTPException(
            status_code=409,
            detail="Профиль для этого пользователя уже существует"
        )

    # 3. Загрузка фото
    photo = upload_photo_to_cloudinary(form.photo, request)

    # 4. Добавление профиля
    return await add_user_profile_to_db(data, session, user["user"].id, photo)


async def validate_user_geo(profile: AddProfile, session: AsyncSession):
    country = await session.scalar(
        select(Country).where(Country.code == profile.country.upper())
    )
    if not country:
        raise ValueError(
            f"Страна с кодом {profile.country} не найдена"
        )
    region = await session.scalar(
        select(Region).where(
            Region.name_ru == profile.region,
            Region.country_code == profile.country.upper()
        )
    )
    if not region:
        raise ValueError(
            f"Регион {profile.region} не найдеен в стране с кодом {profile.country}"
        )

    city = await session.scalar(
        select(City).where(
            City.name_ru == profile.city,
            City.region_id == region.id
        )
    )
    if not city:
        raise ValueError(f"Город '{profile.city}' не найден в регионе '{profile.region}'")


async def get_user_profile_from_db(user_id: int, session: AsyncSession):
    profile = await session.scalar(
        select(Profiles).where(Profiles.user_id == user_id)
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    return profile.to_json


async def get_profiles_from_db(user, session: AsyncSession):
    profiles = await session.scalars(
        select(Profiles).where(Profiles.user_id == user.id)
    )
    if not profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профили не найдены"
        )

    response = []
    for profile in profiles:
        response.append(profile.to_json)
    return response


async def change_user_profile_in_db(form, session: AsyncSession, user, request: Request):
    user_profile = await session.scalar(select(Profiles).where(Profiles.user_id == user.id))
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    for field in ["name", "gender", "orientation", "birthday", "country", "region", "city", "bio"]:
        value = getattr(form, field)
        if value is not None:
            setattr(user_profile, field, value)
    if form.photo:
        print("Получен файл:", form.photo.filename)
        print("Тип:", form.photo.content_type)
        if user_profile.photo_public_id:
            delete_photo_from_cloudinary(user_profile.photo_public_id)
            result = upload_photo_to_cloudinary(form.photo, request)
            user_profile.photo_url = result["photo_url"]
            user_profile.photo_public_id = result["photo_public_id"]

            print("Новый URL:", result["photo_url"])
            print("Старый URL:", user_profile.photo_url)
    await session.commit()
    return {
        "status": 200,
        "photo_url": user_profile.photo_url
    }

