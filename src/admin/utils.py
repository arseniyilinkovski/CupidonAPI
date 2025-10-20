from datetime import datetime, timedelta

from jose import jwt

from src.config import settings


def generate_admin_promotion_token(user_id: int):

    expire = datetime.utcnow() + timedelta(minutes=10)
    payload = {
        "sub": str(user_id),
        "scope": "admin",
        "exp": expire
    }
    token = jwt.encode(payload, settings.get_secret_key(), algorithm=settings.get_algorithm())
    return token



