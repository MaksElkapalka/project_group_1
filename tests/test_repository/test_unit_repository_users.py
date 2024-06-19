import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repository.users import (
    confirmed_email,
    create_user,
    get_user_by_email,
    update_avatar_url,
    update_password,
    update_token,
)
from src.schemas.user import UserSchema


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        user = User(
            id=1,
            username="test_user",
            email="test_user@example.com",
            password="123456",
            confirmed=False,
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email("test_email_1@example.com", self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        user = User(
            id=1,
            username="test_user",
            email="test_user@example.com",
            password="123456",
            confirmed=False,
        )
        body = UserSchema(
            username="test_user", email="test_user@example.com", password="123456"
        )
        result = await create_user(body, self.session)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.password, user.password)

    async def test_update_token(self):
        user = User(
            id=1,
            username="test_user",
            email="test_user@example.com",
            password="123456",
            refresh_token=None,
        )
        token = "test_token"
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        await update_token(user, token, self.session)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = "test_user@example.com"
        user = User(
            id=1,
            username="test_user",
            email="test_user@example.com",
            password="123456",
            confirmed=False,
        )

        with unittest.mock.patch(
            "src.repository.users.get_user_by_email", return_value=user
        ):
            await confirmed_email(email, self.session)

            self.assertTrue(user.confirmed)
            self.session.commit.assert_called_once()

    async def test_update_avatar_url(self):
        email = "test_user@example.com"
        avatar_url = "example.com/avatar.png"
        user = User(
            id=1,
            username="test_user",
            email=email,
            password="123456",
            confirmed=False,
            avatar=None,
        )

        with unittest.mock.patch(
            "src.repository.users.get_user_by_email", return_value=user
        ):
            result = await update_avatar_url(email, avatar_url, self.session)
            self.assertEqual(result.avatar, avatar_url)
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(user)

    async def test_update_password(self):
        user = User(
            id=1,
            username="test_user",
            email="test_user@example.com",
            password="old_password",
            confirmed=False,
        )
        new_password = "new_password"

        result = await update_password(user, new_password, self.session)
        self.assertEqual(result.password, new_password)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(user)
