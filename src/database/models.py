import uuid
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, func, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    refresh_tokens: Mapped[list["RefreshTokens"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    confirmation_token: Mapped[str] = mapped_column(nullable=True)
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    password_reset_confirmation_token: Mapped[str] = mapped_column(nullable=True)


class Profiles(Base):
    __tablename__ = 'profiles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str]  # копия имени для отображения
    age: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String)
    bio: Mapped[str] = mapped_column(String)


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
