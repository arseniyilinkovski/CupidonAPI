from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from src.database.database import async_main, drop_all_tables
from src.routers import register_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_all_tables()
    print("База очищена")
    await async_main()
    print("База создана")
    yield


app = FastAPI(lifespan=lifespan)

register_routers(app)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000)


