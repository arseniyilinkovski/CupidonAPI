from datetime import datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from src.auth.dependencies import oauth2_scheme
from src.config import settings

SECRET_KEY = settings.get_secret_key()
ALGORITHM = settings.get_algorithm()
ACCESS_TOKEN_EXPIRE_MINUTES = settings.get_access_token_expire_minutes()


def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
    return hashed_bytes.decode()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")



