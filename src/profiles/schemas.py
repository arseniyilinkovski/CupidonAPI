from datetime import datetime
from enum import Enum
from fastapi import Form, UploadFile, HTTPException, File
from pydantic import BaseModel, field_validator, ValidationError
from starlette import status

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class Orientation(str, Enum):
    heterosexual = "heterosexual"
    homosexual = "homosexual"
    bisexual = "bisexual"
    other = "other"

class AddProfile(BaseModel):
    name: str
    gender: Gender
    orientation: Orientation
    birthday: datetime
    country: str
    region: str
    city: str
    bio: str

    @field_validator("birthday", mode="before")
    @classmethod
    def parse_birthday(cls, value: str) -> datetime:
        try:
            return datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Дата должна быть в формате 'дд.мм.гггг'")

class FormProfileCreate:
    def __init__(
        self,
        name: str = Form(...),
        gender: str = Form(...),
        orientation: str = Form(...),
        birthday: str = Form(...),
        country: str = Form(...),
        region: str = Form(...),
        city: str = Form(...),
        bio: str = Form(...),
        photo: UploadFile = File(...)
    ):
        self.photo = photo
        print("PHOTO:", photo.filename)
        print("CONTENT TYPE:", photo.content_type)
        try:


            self.model = AddProfile(
                name=name,
                gender=gender,
                orientation=orientation,
                birthday=birthday,
                country=country,
                region=region,
                city=city,
                bio=bio
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=e.errors()
            )
