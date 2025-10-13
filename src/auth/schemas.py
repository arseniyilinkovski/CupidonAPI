from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError


class UserAdd(BaseModel):
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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
