from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import tags as repositories_tag
from src.schemas.tag import TagResponse, TagSchema
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/tags", tags=["tags"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get(
    "/",
    response_model=List[TagResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def get_tags(
    limit: int = Query(default=10, ge=10, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> List[TagResponse]:
    tags = await repositories_tag.get_tags(limit, offset, db, user)
    return tags


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def get_tag(
    tag_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> TagResponse:
    tag = await repositories_tag.get_tag(tag_id, db, user)
    if tag is None:
        raise HTTPException(
            status_code=404,
            detail=f"tag with id {tag_id} not found",
        )
    return tag


@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def create_tag(
    body: TagSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> TagResponse:
    tag = await repositories_tag.create_tag(body, db, user)
    return tag


@router.put(
    "/{tag_id}",
    response_model=TagResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
@router.delete(
    "/{tag_id}",
    response_model=TagResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def delete_tag(
    tag_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> TagResponse:
    tag = await repositories_tag.delete_tag(tag_id, db, user)
    if tag is None:
        raise HTTPException(
            status_code=404,
            detail=f"Tag with id {tag_id} not found",
        )
    return tag
