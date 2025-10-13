from src.geo.constants import REGIONS_BY, CITIES_BY
from src.geo.seed import seed_country, seed_regions, seed_cities


async def seed_all():
    await seed_country("BY", "Belarus", "Беларусь")
    await seed_regions(REGIONS_BY, "BY")
    await seed_cities(CITIES_BY)
    print("Беларусь загружена")

