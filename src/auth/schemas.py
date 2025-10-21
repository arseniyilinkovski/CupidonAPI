

from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError, field_validator

from src.auth.utils import calculate_entropy


class UserAdd(BaseModel):
    email: str
    password: str


    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if not any(c.isdigit() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        entropy = calculate_entropy(value)
        if entropy < 50:
            raise ValueError(f"Пароль ненадеждый (энтропия {entropy} бит). Используйте более сложную комбинацию")
        return value


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
