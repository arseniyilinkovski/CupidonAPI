import asyncio
from datetime import datetime
import uvicorn
from fastapi import FastAPI, Response, Cookie
from src.database.database import async_main, drop_all_tables

app = FastAPI()


@app.get("/hello/{id}")
async def say_hello(id: int):
    return {"status": 200, "id": id}


@app.get("/get_cookie")
async def get_cookie(response: Response):
    now = datetime.now()
    response.set_cookie(key="last_visit", value=str(now))
    return {"message": "Куки установлены"}


@app.get("/get_last_visit")
async def get_last_visit(last_visit: str = Cookie(default="неизвестно")):
    return {"last visit": last_visit}



async def startup():
    await drop_all_tables()
    print("🧹 База очищена")
    await async_main()
    print("✅ Таблицы созданы")

if __name__ == "__main__":
    asyncio.run(startup())
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000)  # ← без reload


