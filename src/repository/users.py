from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        If no user is found, None is returned.

    :param email: str: Get the email from the user
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    """
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(
    user: User, token: str | None = None, db: AsyncSession = Depends(get_db)
) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Pass the user object to the function
    :param token: str | None: Update the refresh token of a user
    :param db: AsyncSession: Get the database session
    :return: None
    """
    if token is not None:
        user.refresh_token = token
        await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function marks a user as confirmed in the database.

    :param email: str: Specify the email address of the user to confirm
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Find the user in the database
    :param url: str | None: Specify that the url parameter can be either a string or none
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(
    user: User, new_password: str, db: AsyncSession = Depends(get_db)
) -> None:
    """
    The update_password function updates the password of a user.
        Args:
            user (User): The User object to update.
            new_password (str): The new password for the User object.
        Returns: None

    :param user: User: Pass in the user object that is being updated
    :param new_password: str: Pass in the new password for the user
    :param db: AsyncSession: Pass in the database session to the function
    :return: The user object
    """
    user.password = new_password
    await db.commit()
    await db.refresh(user)
    return user
