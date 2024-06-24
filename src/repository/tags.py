from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag, Image, User, image_tag_table
from src.schemas.tag import TagSchema


async def create_tag(body: TagSchema, db: AsyncSession) -> Tag:
    new_tag = Tag(name=body.name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag


async def get_tags(skip: int, limit: int, db: AsyncSession) -> List[Tag]:
    stmt = select(Tag).offset(skip).limit(limit)
    tags = await db.execute(stmt)
    return tags.scalars().all()


async def get_tag(tag_name: str, db: AsyncSession) -> Optional[Tag]:
    stmt = select(Tag).filter_by(name=tag_name)
    tag = await db.execute(stmt)
    return tag.scalar_one_or_none()


async def update_tag(tag_id: int, body: TagSchema, db: AsyncSession):
    stmt = select(Tag).filter_by(id=tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if tag:
        tag.name = body.name
        await db.commit()
        await db.refresh(tag)
    return tag


async def remove_tag(tag_id: int, db: AsyncSession):
    stmt = select(Tag).filter_by(id=tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if tag:
        await db.delete(tag)
        await db.commit()
    return tag


async def add_tag_for_image(
    tag_name: str, image_id: int, user: User, db: AsyncSession
) -> Optional[Tag]:
    # Пошук зображення за ID, що належить користувачеві
    stmt = select(Image).filter_by(id=image_id, user_id=user.id)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()

    if image:
        # Перевірка наявності тега
        tag = await get_tag(tag_name, db)
        if not tag:
            # Створення нового тега, якщо його не існує
            tag_name = TagSchema(name=tag_name)
            tag = await create_tag(tag_name, db)
            print(tag.id, "*" * 100)

        # Додавання тегу до зображення через проміжну таблицю
        await db.execute(
            image_tag_table.insert().values(image_id=image.id, tag_id=tag.id)
        )
        await db.commit()
        await db.refresh(tag)

        return tag

    return None
