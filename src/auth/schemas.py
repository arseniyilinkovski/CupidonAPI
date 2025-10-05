from datetime import datetime

from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError


class UserAdd(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class FormUserLogin:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...)
    ):
        try:
            self.model = UserLogin(email=username, password=password)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())


class User(UserAdd):
    pass #TODO Дописать схему для юзера