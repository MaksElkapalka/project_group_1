from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag, Image, User
from src.schemas.tag import TagSchema


async def create_tag(body: TagSchema, db: AsyncSession) -> Tag:
    new_tag = Tag(**body.model_dump(exclude_unset=True))
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


async def add_tag_for_image(tag_name: str, image_id: int, user: User, db: AsyncSession):
    stmt = select(Image).filter_by(id=image_id, user=user)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()
    if image:
        tag = await get_tag(tag_name, db)
        if tag:
            if tag not in image.tags:
                image.tags.append(tag)
                db.commit()
            return tag
        else:
            new_tag = await create_tag(TagSchema(name=tag_name), db)
            image.tags.append(new_tag)
            db.commit()
            return new_tag
    return image
