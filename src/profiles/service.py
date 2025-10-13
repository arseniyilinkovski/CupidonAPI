from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Profiles, Country, Region, City
from src.profiles.schemas import AddProfile


async def add_user_profile_to_db(data: AddProfile, session: AsyncSession, user_id: int):
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
        bio=data.bio
    )
    session.add(new_profile)
    await session.commit()
    return {
        "message": "Профиль успешно создан",
        "age": new_profile.age
    }


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