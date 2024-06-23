from fastapi import Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import Comment, User
from src.schemas.comments import CommentCreate, CommentUpdate
from src.conf import messages


async def get_comment(
        comment_id: int,
        db: AsyncSession = Depends(get_db)
) -> None:
    """
    The get_comment function returns a comment object from the database based on the comment's id provided.
        If no comment is found, None is returned.

    :param comment_id: int: Comment's id in database
    :param db: AsyncSession: Pass in the database session
    :return: A comment object
    """
    stmt = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    return comment


async def create_comment(
        current_user: User,
        body: CommentCreate,
        db: AsyncSession = Depends(get_db)):
    """
    The create_comment function creates a new comment.

    :param body: CommentCreate: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :return: A Comment object
    """
    new_comment = Comment(**body.dict(), user_id=current_user.id)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def update_comment(
    comment_id: int,
    coment_update: CommentUpdate,
    current_user: User,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    The update_comment function updates the comments.

    :param comment_id: int: Pass in the comment object that is being updated
    :param coment_update: CommentUpdate: Pass in the new data for the comment updating
    :param current_user: User: Comment creator
    :param db: AsyncSession: Pass in the database session to the function
    :return: The comment object
    """
    stmt = select(Comment).filter_by(id=comment_id, user_id=current_user.id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        comment.name = coment_update.name
        await db.commit()
        await db.refresh(comment)
    return comment


async def delete_comment(
    comment_id: int,
    current_user: User,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    The remove_comment function removes comment from database.

    :param comment_id: int: Pass in the comment object that is being updated
    :param current_user: User: Comment creator
    :param db: AsyncSession: Pass in the database session to the function
    :return: The comment object
    """
    stmt = select(Comment).filter_by(id=comment_id, user_id=current_user.id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment