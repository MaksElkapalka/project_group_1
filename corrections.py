#   Модель

class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="images", lazy="joined"
    )
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="image", cascade="all, delete-orphan", lazy="selectin")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary=image_tag_table, back_populates="images", lazy="selectin")


#  Репозиторій

async def get_all_images(limit: int, 
                         offset: int,
                         db: AsyncSession):
    stmt = select(Image).options(selectinload(Image.comments), selectinload(Image.tags)).offset(offset).limit(limit)
    result = await db.execute(stmt)
    images = result.scalars().all()
    return images


#  Роут

@router.get("/show/", response_model=list[ImageResponse])
async def get_all_images(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=10), db: AsyncSession = Depends(get_db)):
    images = await repository_images.get_all_images(limit, offset, db)
    response_images = []
    for image in images:
        response_images.append(ImageResponse(
            id=image.id,
            url=image.url,
            description=image.description,
            tags=[tag.name for tag in image.tags],  # assuming `name` is the field for tag name
            comments=[comment.text for comment in image.comments]  # assuming `text` is the field for comment text
        ))
    return response_images
