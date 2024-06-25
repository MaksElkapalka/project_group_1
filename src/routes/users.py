import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import users as repositories_users
from src.schemas.user import (
    UserResponse,
    UserUpdate,
    UserPublicResponse,
    UserActiveResponse
)
from src.services.auth import auth_service, role_required

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/profile/{email}",
    response_model=UserPublicResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_user_profile(email: str, db: AsyncSession = Depends(get_db)) -> User:
    """
    Get user profile by email

    :param email: Email for the user
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object
    """

    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
    user: User = Depends(auth_service.get_current_active_user),
) -> User:
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Get the current user
    :return: The user object
    """
    return user


@router.put(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user),
) -> User:
    """
    The update_current_user function is a dependency that will be injected into the
        update_current_user endpoint. It uses the auth_service to update the current user information,
        and returns it if found.

    :param user_update: UserUpdate: Data for user's info updating
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The user object
    """
    current_user = await db.merge(current_user)
    user = await repositories_users.update_user(current_user, user_update, db)
    return user


@router.put("/ban/{email}",
            response_model=UserActiveResponse,
            dependencies=[Depends(role_required(["admin", "moderator"]))]
)
async def bun_user(
    email: str,
    db: AsyncSession = Depends(get_db),):
    """
    Ban user by email, setting status for user inactive, depends on user's role, should be admin.

    :param email: Email of the user to ban
    :param db: AsyncSession: Pass the database session to the function
    : return: Banned user profile
    """
    try:
        user = await repositories_users.set_user_status(email, False, db)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/unban/{email}",
            response_model=UserActiveResponse,
            dependencies=[Depends(role_required(["admin", "moderator"]))]
)
async def unbun_user(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Unban user by email, setting status for user active, depends on user's role, should be admin

    :param email: Email of the user to unban
    :param db: AsyncSession: Pass the database session to the function
    : return: Unbanned user profile
    """
    try:
        user = await repositories_users.set_user_status(email, True, db)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def avatar_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The avatar_user function is used to upload a user's avatar image.
        The function takes in an UploadFile object, which contains the file that was uploaded by the user.
        It also takes in a User object, which is obtained from the auth_service module and represents the current logged-in user.
        Finally, it also accepts an AsyncSession object for interacting with our database.

    :param file: UploadFile: Get the file from the request
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Pass the database session to the function
    :param : Get the current user from the database
    :return: An object of type user
    """
    public_id = f"restapp/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user


@router.put("/role/{email}", response_model=UserResponse, dependencies=[Depends(role_required("admin"))])
async def set_role(
    email: str,
    update_role: Role,
    db: AsyncSession = Depends(get_db)
):
    """
    Set role for user

    :param email: Email of the user to setting role
    :param update_role: UserRoleUpdate: Role to change for user
    :param db: AsyncSession: Pass the database session to the function
    :param admin: User: current user with admin role
    : return: Unbanned user profile
    """
    user = await repositories_users.update_user_role(email, update_role, db)
    return user
