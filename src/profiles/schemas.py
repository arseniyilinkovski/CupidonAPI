from datetime import datetime
from enum import Enum

import pycountry
from pydantic import BaseModel, field_validator

from src.profiles.utils import get_valid_regions

REVERSE_COUNTRIES = {
    country.name.lower(): country.alpha_2
    for country in pycountry.countries
}

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


    @field_validator("birthday", mode="before")
    @classmethod
    def parse_birthday(cls, value: str) -> datetime:
        try:
            return datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Дата должна быть в формате 'дд.мм.гггг' ")

    country: str
    region: str
    city: str
    bio: str



