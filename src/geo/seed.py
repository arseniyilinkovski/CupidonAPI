from sqlalchemy import select

from src.database.database import async_session
from src.database.models import Country, Region, City


async def seed_country(code: str, name_en: str, name_ru: str):
    async with async_session() as session:
        belarus = Country(
            code=code,
            name_en=name_en,
            name_ru=name_ru
        )
        session.add(belarus)
        await session.commit()


async def seed_regions(regions: list, country_code: str):
    async with async_session() as session:
        for name_en, name_ru in regions:
            region = Region(
                name_en=name_en,
                name_ru=name_ru,
                country_code=country_code
            )
            session.add(region)
        await session.commit()


async def seed_cities(cities: dict):
    async with async_session() as session:
        for region_ru, cities in cities.items():
            region = await session.scalar(
                select(Region).where(Region.name_ru == region_ru)
            )
            if not region:
                continue
            for city_name in cities:
                city = City(
                    name_en=city_name,
                    name_ru=city_name,
                    region_id=region.id
                )
                session.add(city)
        await session.commit()

