from fastapi import FastAPI

from src.auth.routers import auth_router
from src.profiles.routers import profiles_router


def register_routers(app: FastAPI):
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
