from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.database.database import  drop_all_tables
from src.geo.core import seed_all
from src.routers import register_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.config_cloudinary()
    # await seed_all()
    # await drop_all_tables()
    # print("База очищена")
    yield


app = FastAPI(lifespan=lifespan)

register_routers(app)


if __name__ == "__main__":

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000)


