from fastapi import FastAPI

from src.auth.routers import auth_router


def register_routers(app: FastAPI):
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
