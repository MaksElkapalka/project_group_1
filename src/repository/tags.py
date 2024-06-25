from typing import List, Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag, Image, User, image_tag_table
from src.schemas.tag import TagSchema


# async def create_tag(body: TagSchema, db: AsyncSession) -> Tag:
#     new_tag = Tag(name=body.name)
#     db.add(new_tag)
#     await db.commit()
#     await db.refresh(new_tag)
#     return new_tag


async def create_tags(body: TagSchema, db: AsyncSession) -> List[Tag]:
    existing_tags_query = await db.execute(
        select(Tag).where(Tag.name.in_(body.tag_list))
    )
    existing_tags = {tag.name for tag in existing_tags_query.scalars().all()}
    new_tags = []
    for tag_name in body.tag_list:
        if tag_name not in existing_tags:
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            new_tags.append(new_tag)

    await db.commit()
    for new_tag in new_tags:
        await db.refresh(new_tag)
    return new_tags


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


"   НЕ ВИДАЛЯЙТЕ ЦЮ ФУНКЦІЮ"
# async def add_tag_for_image(
#     tag_name: str, image_id: int, user: User, db: AsyncSession
# ) -> Optional[Tag]:
#     # Пошук зображення за ID, що належить користувачеві
#     stmt = select(Image).filter_by(id=image_id, user_id=user.id)
#     result = await db.execute(stmt)
#     image = result.scalar_one_or_none()

#     if image:
#         # Перевірка наявності тега
#         tag = await get_tag(tag_name, db)
#         if not tag:
#             new_tag_data = TagSchema(name=tag_name)
#             tag = await create_tag(new_tag_data, db)
#         stmt = insert(image_tag_table).values(image_id=image_id, tag_id=tag.id)
#         await db.execute(stmt)
#         await db.commit()
#         return tag

#     return None


async def add_tags_for_image(
    tags_data: TagSchema, image_id: int, user: User, db: AsyncSession
) -> Optional[List[Tag]]:
    # Пошук зображення за ID, що належить користувачеві
    stmt = select(Image).filter_by(id=image_id, user_id=user.id)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()

    if image:
        # Створення тегів, якщо їх ще не існує
        created_tags = await create_tags(tags_data, db)

        # Додавання зв'язків між зображенням та створеними тегами у проміжну таблицю
        values = [{"image_id": image_id, "tag_id": tag.id} for tag in created_tags]
        stmt = image_tag_table.insert().values(values)
        await db.execute(stmt)
        await db.commit()

        return created_tags

    return None
