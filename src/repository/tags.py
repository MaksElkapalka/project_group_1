from typing import List, Optional

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Image, Tag, User, image_tag_table
from src.schemas.tag import TagSchema

# async def create_tag(body: TagSchema, db: AsyncSession) -> Tag:
#     new_tag = Tag(name=body.name)
#     db.add(new_tag)
#     await db.commit()
#     await db.refresh(new_tag)
#     return new_tag


async def create_tags(body: TagSchema, db: AsyncSession) -> List[Tag]:
    """The create_tags function creates a new tags.

    Args:
        body (TagSchema): Validate the request body.
        db (AsyncSession): Pass in the database session.

    Returns:
        List[Tag]: List of created tags.
    """
    existing_tags_query = await db.execute(
        select(Tag).where(Tag.name.in_(body.tag_list))
    )
    existing_tags = {tag.name for tag in existing_tags_query.scalars().all()}
    tags_in_db = []
    new_tags = []
    for tag_name in body.tag_list:
        if tag_name not in existing_tags:
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            new_tags.append(new_tag)
        else:
            tags_in_db.append(tag_name)

    await db.commit()
    for new_tag in new_tags:
        await db.refresh(new_tag)
    for tag_name in tags_in_db:
        tag = await get_tag(tag_name, db)
        new_tags.append(tag)
    return new_tags


async def get_tags(skip: int, limit: int, db: AsyncSession) -> List[Tag]:
    """The get_tags function displays existing tags.

    Args:
        skip (int): The number of images to skip.
        limit (int): The maximum number of images to return.
        db (AsyncSession): Pass in the database session.

    Returns:
        List[Tag]: List of all tags
    """
    stmt = select(Tag).offset(skip).limit(limit)
    tags = await db.execute(stmt)
    return tags.scalars().all()


async def get_tag(tag_name: str, db: AsyncSession) -> Optional[Tag]:
    """The get_tag function displays a tag by given name.

    Args:
        tag_name (str): Pass in the tag object in database.
        db (AsyncSession): Pass in the database session.

    Returns:
        Optional[Tag]: Existing tag
    """
    stmt = select(Tag).filter_by(name=tag_name)
    tag = await db.execute(stmt)
    return tag.scalar_one_or_none()


async def update_tag(tag_id: int, body: TagSchema, db: AsyncSession):
    """The update_tag function updates a tag.

    Args:
        tag_id (int): Pass in the tag object in database.
        body (TagSchema): Validate the request body.
        db (AsyncSession): Pass in the database session.

    Returns:
        Tag: Updated tag.
    """
    stmt = select(Tag).filter_by(id=tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if tag:
        tag.name = body.name
        await db.commit()
        await db.refresh(tag)
    return tag


async def remove_tag(tag_id: int, db: AsyncSession):
    """The remove_tag function removes a tag.

    Args:
        tag_id (int): Pass in the tag object in database.
        db (AsyncSession): Pass in the database session.

    Returns:
        Tag: Removed tag
    """
    stmt = select(Tag).filter_by(id=tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if tag:
        await db.delete(tag)
        await db.commit()
    return tag


async def add_tags_for_image(
    tags_data: TagSchema, image_id: int, user: User, db: AsyncSession
) -> Optional[List[Tag]]:
    """The add_tags_for_image function adds tags to image.

    Args:
        tags_data (TagSchema): List of tags.
        image_id (int): Pass in the image object in database.
        user (User): Current user.
        db (AsyncSession): Pass in the database session.

    Returns:
        Optional[List[Tag]]: List of tags.
    """
    # Пошук зображення за ID, що належить користувачеві
    stmt = select(Image).filter_by(id=image_id, user_id=user.id)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()

    if image:
        # Створення тегів, якщо їх ще не існує
        created_tags = await create_tags(tags_data, db)

        # Додавання зв'язків між зображенням та створеними тегами у проміжну таблицю
        values = []
        for tag in created_tags:  # перевірка чи тег вже доданий до кортинки
            exists_query = select(
                exists()
                .where(image_tag_table.c.image_id == image_id)
                .where(image_tag_table.c.tag_id == tag.id)
            )
            exists_result = await db.execute(exists_query)
            if not exists_result.scalar():
                values.append({"image_id": image_id, "tag_id": tag.id})

        if values:
            stmt = image_tag_table.insert().values(values)
            try:
                await db.execute(stmt)
                await db.commit()
            except IntegrityError:
                await db.rollback()  # обробка помилки якщо тег вже доданий до кортинки
                pass

        return created_tags

    return None
