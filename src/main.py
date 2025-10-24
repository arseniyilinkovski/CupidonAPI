import os
import urllib
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from nsfw_detector import predict
from tensorflow import keras

from src.config import settings
from src.database.database import  drop_all_tables
from src.geo.core import seed_all
from src.routers import register_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.config_cloudinary()
    h5_path = "ai-models/nsfw_model.h5"
    saved_model_path = "ai-models/nsfw_model_finetuned.h5"

    # 🔧 1. Скачиваем .h5, если его нет
    if not os.path.exists(h5_path):
        print("📥 Скачиваю NSFW-модель...")
        os.makedirs(os.path.dirname(h5_path), exist_ok=True)
        url = "https://s3.amazonaws.com/nsfwdetector/nsfw.299x299.h5"
        urllib.request.urlretrieve(url, h5_path)
        print("✅ Модель скачана")

    # 🔁 2. Конвертируем в SavedModel, если ещё не конвертирована
    if not os.path.exists(saved_model_path):
        print("🔄 Конвертация .h5 → SavedModel...")
        keras_model = keras.models.load_model(h5_path)
        keras_model.save(saved_model_path)
        print("✅ SavedModel готов")

    # 🚀 3. Загружаем модель в FastAPI
    app.state.nsfw_model = predict.load_model(saved_model_path)
    # await seed_all()
    # await drop_all_tables()
    # print("База очищена")
    yield


app = FastAPI(lifespan=lifespan)

register_routers(app)


if __name__ == "__main__":

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000)


