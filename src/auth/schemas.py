from datetime import datetime

from pydantic import BaseModel


class UserAdd(BaseModel):
    name: str
    email: str
    password: str


class User(UserAdd):
    pass #TODO Дописать схему для юзера