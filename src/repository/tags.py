from datetime import date, timedelta
from typing import Optional

from sqlalchemy import and_, extract, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag, User
from src.schemas.tag import TagSchema


async def get_tags(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Tag).filter_by(user_id=user.id).offset(offset).limit(5)
    tags = await db.execute(stmt)
    return tags.scalars().all()


async def get_tag(tag_id: int, db: AsyncSession, user: User):
    stmt = select(Tag).filter_by(id=tag_id, user_id=user.id)
    tag = await db.execute(stmt)
    return tag.scalar_one_or_none()


async def crete_tag(body: TagSchema, db: AsyncSession, user: User):
    tag = Tag(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


# async def update_contact(
#     tag_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User
# ):
#     """
#     The update_contact function updates a tag in the database.

#     :param tag_id: int: Get the tag that needs to be updated
#     :param body: ContactUpdateSchema: Validate the data sent in the request body
#     :param db: AsyncSession: Pass in a database session to the function
#     :param user: User: Get the user id from the token
#     :return: A tag object or none
#     """
#     stmt = select(Tag).filter_by(id=tag_id, user_id=user.id)
#     result = await db.execute(stmt)
#     tag = result.scalar_one_or_none()
#     if tag:
#         tag.first_name = body.first_name
#         tag.last_name = body.last_name
#         tag.email = body.email
#         tag.phone_number = body.phone_number
#         tag.birthday = body.birthday
#         tag.additional_info = body.additional_info
#         await db.commit()
#         await db.refresh(tag)
#     return tag


async def delete_tag(tag_id: int, db: AsyncSession, user: User):
    stmt = select(Tag).filter_by(id=tag_id, user_id=user.id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()

    if tag is None:
        return None

    await db.delete(tag)
    await db.commit()
    return tag


async def search_tags(
    first_name: Optional[str],
    last_name: Optional[str],
    email: Optional[str],
    db: AsyncSession,
    user: User,
):
    query = select(Tag).filter_by(user_id=user.id)

    filters = []
    if first_name:
        filters.append(Tag.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Tag.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Tag.email.ilike(f"%{email}%"))

    if filters:
        query = query.filter(or_(*filters))

    result = await db.execute(query)
    return result.scalars().all()


async def get_birthdays(db: AsyncSession, user: User):
    today = date.today()
    upcoming_date = today + timedelta(days=7)

    query = select(Tag).filter(
        Tag.user_id == user.id,
        or_(
            and_(
                extract("month", Tag.birthday) == today.month,
                extract("day", Tag.birthday) >= today.day,
            ),
            and_(
                extract("month", Tag.birthday) == upcoming_date.month,
                extract("day", Tag.birthday) <= upcoming_date.day,
            ),
        ),
    )

    result = await db.execute(query)
    return result.scalars().all()