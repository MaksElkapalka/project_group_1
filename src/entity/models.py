from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func, Text, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

default_avatar_url = (
    "https://res.cloudinary.com/restapp/image/upload/v1717342921/restapp/default.png"
)


class Base(DeclarativeBase):
    pass


photo_tags_table = Table(
    "photo_tags",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    photos: Mapped[list['Photo']] = relationship('Photo', secondary=photo_tags_table, back_populates='tags')


class Photo(Base):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="photos", lazy="joined"
    )
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="photo", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary=photo_tags_table, back_populates="photos")


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    photo: Mapped['Photo'] = relationship("Photo", back_populates='comments')
    user: Mapped['User'] = relationship("User", back_populates='comments')


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default='user')
    access_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[str] = mapped_column(
        String(255), nullable=True, default=default_avatar_url
    )
    photos: Mapped[list["Photo"]] = relationship('Photo', back_populates='user')
    comments: Mapped[list["Comment"]] = relationship('Comment', back_populates='user')
