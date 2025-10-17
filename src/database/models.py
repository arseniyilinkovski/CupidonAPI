import uuid
from datetime import datetime, date
from sqlalchemy import Integer, String, ForeignKey, func, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class GeoBase(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    refresh_tokens: Mapped[list["RefreshTokens"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    confirmation_token: Mapped[str] = mapped_column(nullable=True)
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    password_reset_confirmation_token: Mapped[str] = mapped_column(nullable=True)
    password_reset_confirmation_token_expires: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Profiles(Base):
    __tablename__ = 'profiles'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True, primary_key=True)
    name: Mapped[str]
    gender: Mapped[str]
    orientation: Mapped[str]
    birthday: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime)
    country: Mapped[str]
    region: Mapped[str]
    city: Mapped[str]
    bio: Mapped[str] = mapped_column(String)

    @property
    def to_json(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "gender": self.gender,
            "orientation": self.orientation,
            "age": self.age,
            "last_active_at": self.last_active_at,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "bio": self.bio
        }

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.birthday.year - (
            (today.month, today.day) < (self.birthday.month, self.birthday.day)
        )


class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: uuid.uuid4().hex
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    user: Mapped["Users"] = relationship(back_populates="refresh_tokens")


class Country(GeoBase):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(primary_key=True)
    name_en: Mapped[str]
    name_ru: Mapped[str]


class Region(GeoBase):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_en: Mapped[str]
    name_ru: Mapped[str]
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"))

    country: Mapped["Country"] = relationship(backref="regions")


class City(GeoBase):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_en: Mapped[str]
    name_ru: Mapped[str]
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"))

    region: Mapped["Region"] = relationship(backref="cities")
