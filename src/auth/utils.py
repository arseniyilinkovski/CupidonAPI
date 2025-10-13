import uuid
from datetime import datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException
from fastapi_mail import MessageSchema, FastMail
from jose import jwt, JWTError

from src.auth.dependencies import oauth2_scheme
from src.config import settings

SECRET_KEY = settings.get_secret_key()
ALGORITHM = settings.get_algorithm()
ACCESS_TOKEN_EXPIRE_MINUTES = settings.get_access_token_expire_minutes()


def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
    return hashed_bytes.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_confirmation_token() -> str:
    return uuid.uuid4().hex


async def send_confirmation_email(
        email: str,
        token: str,
        subject: str,
        body: str,
        route: str
):

    URL = settings.get_URL()
    message = MessageSchema(
        subject=f"{subject}",
        recipients=[email],
        body=f"""
                 <h3>Добро пожаловать!</h3>
        <p>{body}</p>
        <a href="{URL}{route}?token={token}">Подтвердить email</a>
            """,
        subtype="html"
    )
    fm = FastMail(settings.config_smtp_provider())
    await fm.send_message(message)
