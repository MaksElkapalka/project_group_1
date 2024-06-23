from typing import List, Optional
from sqlalchemy.orm import Session
from src.entity.models import Tag, Image
from src.schemas.tag import TagSchema

def create_tag(body: TagSchema, db: Session) -> Tag:
    new_tag = Tag(**body.dict())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

def add_tag(photo_id: int, tag_name: str, user_id: int, db: Session) -> Optional[Tag]:
    photo = db.query(Image).filter(Image.id == photo_id, Image.user_id == user_id).first()
    if not photo:
        return None

    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if tag:
        if tag not in photo.tags:
            photo.tags.append(tag)
            db.commit()
        return tag
    else:
        new_tag = create_tag(TagSchema(name=tag_name), db)
        photo.tags.append(new_tag)
        db.commit()
        return new_tag
