from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

default_avatar_url = (
    "https://res.cloudinary.com/restapp/image/upload/v1717342921/restapp/default.png"
)


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(Date)
    additional_info: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="contacts", lazy="joined"
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", back_populates="user", cascade="all, delete-orphan"
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[str] = mapped_column(
        String(255), nullable=True, default=default_avatar_url
    )
