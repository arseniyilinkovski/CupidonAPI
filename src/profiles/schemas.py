from datetime import datetime
from enum import Enum
from typing import Optional

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


class FormProfileUpdate:
    def __init__(
        self,
        name: Optional[str] = Form(None),
        gender: Optional[str] = Form(None),
        orientation: Optional[str] = Form(None),
        birthday: Optional[str] = Form(None),
        country: Optional[str] = Form(None),
        region: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        photo: Optional[UploadFile] = File(None)
    ):
        self.name = name or None
        self.gender = self.parse_enum(Gender, gender)
        self.orientation = self.parse_enum(Orientation, orientation)
        self.birthday = self.parse_birthday(birthday)
        self.country = country or None
        self.region = region or None
        self.city = city or None
        self.bio = bio or None
        self.photo = photo

    def parse_birthday(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Дата должна быть в формате 'дд.мм.гггг'"
            )

    def parse_enum(self, enum_cls, value: Optional[str]):
        if not value:
            return None
        try:
            return enum_cls(value)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимое значение: {value}. Ожидается одно из: {[e.value for e in enum_cls]}"
            )

