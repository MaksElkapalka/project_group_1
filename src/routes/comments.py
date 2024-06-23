from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.entity.models import Comment, User
from src.repository import comments as repositories_comments
from src.schemas.comments import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from src.services.auth import auth_service, auth_decorator


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/create", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    The create_comment function creates a new comment.

    :param comment: CommentCreate: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Comment's creator
    :return: A Comment object
    """
    new_comment = await repositories_comments.create_comment(comment, db, current_user)
    return new_comment


@router.put("/update/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    The create_comment function creates a new comment.

    :param comment_id: Existing comments id
    :param comment: CommentUpdate: Validate the request body for comment updating
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Comment's creator
    :return: A Comment object
    """
    new_comment = await repositories_comments.update_comment(comment_id, comment, current_user, db)
    if new_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)
    return new_comment


@router.delete("/delete/{comment_id}", response_model=CommentResponse)
def delete_comment(

    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    The create_comment function creates a new comment.

    :param comment_id: Existing comments id
    :param comment: CommentUpdate: Validate the request body for comment updating
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Comment's creator
    :return: A Comment object
    """
    new_comment = repositories_comments.delete_comment(comment_id, current_user, db)
    if new_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)
    return new_comment