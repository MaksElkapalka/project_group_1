import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy import select

from src.entity.models import Image, User
from src.schemas.image import ImageUpdateSchema
from src.repository.images import (
    upload_image,
    update_image,
    get_all_images,
    get_image,
    delete_image,
    get_transformed_url,
    get_foravatar_url,
)


class TestImageRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(
            id=1,
            username="test_user",
            email="test_user@example.com",
            password="123456",
            confirmed=True,
            avatar="example.com/avatar.png",
            role=1,
            image_count=0,
        )

    @patch("cloudinary.uploader.upload")
    async def test_upload_image(self, mock_upload):
        # Налаштування моку cloudinary.uploader.upload
        mock_upload.return_value = {"url": "http://example.com/image.jpg"}

        # Мок файлу
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_image.jpg"
        mock_file.content_type = "image/jpeg"
        mock_file.read.return_value = b"file_content"

        # Виклик функції upload_image
        image = await upload_image(
            file=mock_file, description="Test Image", db=self.session, user=self.user
        )

        # Перевірка результатів
        self.assertEqual(image.url, "http://example.com/image.jpg")
        self.assertEqual(image.description, "Test Image")
        self.assertEqual(image.user_id, self.user.id)

    async def test_update_image(self):
        body = ImageUpdateSchema(description="New Description")
        image = Image(
            id=1,
            description="Old Description",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Створення асинхронного мока для результату запиту
        mocked_image = MagicMock()
        mocked_image.unique.return_value.scalar_one_or_none = MagicMock()
        mocked_image.scalar_one_or_none.return_value = body
        self.session.execute.return_value = mocked_image

        updated_image = await update_image(image_id=1, body=body, db=self.session)

        self.assertEqual(updated_image.description, "New Description")
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_with(updated_image)

    async def test_get_all_images(self):
        limit = 10
        offset = 0
        images = [
            Image(
                id=i,
                description=f"Image {i}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(5)
        ]
        mocked_images = MagicMock()
        mocked_images.unique.return_value.scalars.return_value.all.return_value = images
        self.session.execute.return_value = mocked_images
        result = await get_all_images(limit, offset, self.session)
        self.assertEqual(result, images)
        self.assertEqual(len(result), len(images))

    async def test_get_image(self):
        image = Image(
            id=1,
            description="Test Image",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user_id=self.user.id,
        )

        mocked_image = MagicMock()
        mocked_image.unique.return_value.scalar_one_or_none.return_value = image
        self.session.execute.return_value = mocked_image
        result = await get_image(1, self.session, self.user)
        self.assertEqual(result, image)

    @patch("cloudinary.uploader.destroy")
    async def test_delete_image(self, mock_destroy):
        images = [
            Image(
                id=i,
                description=f"Image {i}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(1, 6)
        ]
        print(len(images))
        self.session.execute.side_effect = [
            MagicMock(return_value=images),
            MagicMock(return_value=self.user),
        ]
        mock_destroy.return_value = {"result": "ok"}
        deleted_image = await delete_image(image_id=1, db=self.session)
        mock_destroy.assert_called_once()
        self.assertEqual(len(deleted_image), len(images))
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(self.user)

    # @patch("cloudinary.CloudinaryImage.build_url")
    # async def test_get_transformed_url(self, mock_build_url):
    #     mock_build_url.return_value = "http://example.com/transformed_image.jpg"

    #     result = await get_transformed_url(
    #         "http://example.com/image.jpg", {"crop": "fill"}, self.user, self.session
    #     )

    #     self.assertEqual(result, "http://example.com/transformed_image.jpg")
    #     self.session.add.assert_called()
    #     self.session.commit.assert_called_once()
    #     self.session.refresh.assert_called()

    # @patch("cloudinary.CloudinaryImage.build_url")
    # async def test_get_foravatar_url(self, mock_build_url):
    #     mock_build_url.return_value = "http://example.com/transformed_image.png"

    #     result = await get_foravatar_url(
    #         "http://example.com/image.jpg", {"crop": "fill"}, self.user, self.session
    #     )

    #     self.assertEqual(result, "http://example.com/transformed_image.png")
    #     self.session.add.assert_called()
    #     self.session.commit.assert_called_once()
    #     self.session.refresh.assert_called()


if __name__ == "__main__":
    unittest.main()
