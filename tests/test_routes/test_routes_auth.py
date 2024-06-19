from unittest.mock import ANY, Mock, patch, AsyncMock

import pytest
from sqlalchemy import select
from src.entity.models import User
from tests.conftest import TestingSessionLocal
from src.services.auth import auth_service
from src.conf import messages


class TestSignup:
    user_data = {
        "username": "test_user_auth",
        "email": "test_email_auth@example.com",
        "password": "12345678",
    }

    @staticmethod
    def setup_monkeypatch(monkeypatch):
        with patch.object(auth_service, "cache") as redis_mock:
            redis_mock.get.return_value = None
            monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
            monkeypatch.setattr(
                "fastapi_limiter.FastAPILimiter.identifier", AsyncMock()
            )
            monkeypatch.setattr(
                "fastapi_limiter.FastAPILimiter.http_callback", AsyncMock()
            )

    def test_signup(self, client, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        mock_send_email = Mock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
        response = client.post("api/auth/signup", json=self.user_data)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["username"] == self.user_data["username"]
        assert data["email"] == self.user_data["email"]
        assert "password" not in data
        assert "avatar" in data

    def test_repeat_signup(self, client, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        mock_send_email = Mock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
        response = client.post("api/auth/signup", json=self.user_data)
        assert response.status_code == 409, response.text
        data = response.json()
        assert data["detail"] == messages.ACCOUNT_EXIST

    @pytest.mark.asyncio
    async def test_not_confirmed_login(self, client, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        mock_send_email = Mock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
        async with TestingSessionLocal() as session:
            current_user = await session.execute(
                select(User).where(User.email == self.user_data.get("email"))
            )
            current_user = current_user.scalar_one_or_none()
            if current_user:
                current_user.confirmed = False
                await session.commit()
        response = client.post(
            "api/auth/login",
            data={
                "username": self.user_data.get("email"),
                "password": self.user_data.get("password"),
            },
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == messages.NOT_CONFIRMED

    @pytest.mark.asyncio
    async def test_login(self, client, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        async with TestingSessionLocal() as session:
            current_user = await session.execute(
                select(User).where(User.email == self.user_data.get("email"))
            )
            current_user = current_user.scalar_one_or_none()
            if current_user:
                current_user.confirmed = True
                await session.commit()

        response = client.post(
            "api/auth/login",
            data={
                "username": self.user_data.get("email"),
                "password": self.user_data.get("password"),
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

    def test_wrong_password_login(self, client, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        response = client.post(
            "api/auth/login",
            data={"username": self.user_data.get("email"), "password": "password"},
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == messages.INVALID_PASSWORD

    def test_wrong_email_login(self, client, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        response = client.post(
            "api/auth/login",
            data={
                "username": "wrong_email",
                "password": self.user_data.get("password"),
            },
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == messages.INVALID_EMAIL

    @pytest.mark.asyncio
    async def test_confirmed_email(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token

        response = client.get(f"api/auth/confirmed_email/{token}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == messages.ACCOUNT_CONFIRMED

    @pytest.mark.asyncio
    async def test_already_confirmed_email(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token

        response = client.get(f"api/auth/confirmed_email/{token}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == messages.ALREADY_CONFIRMED

    @pytest.mark.asyncio
    async def test_confirmed_email_not_found(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        mock_get_email_from_token = AsyncMock(return_value=None)
        monkeypatch.setattr(
            auth_service, "get_email_from_token", mock_get_email_from_token
        )
        response = client.get(f"api/auth/confirmed_email/{token}")
        assert response.status_code == 400, response.text
        data = response.json()
        assert data["detail"] == messages.INVALID_EMAIL

    @pytest.mark.asyncio
    async def test_password_reset_request(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        mock_send_email = AsyncMock()
        monkeypatch.setattr(
            "src.routes.auth.send_reset_password_email", mock_send_email
        )
        mock_generate_token = Mock(return_value=token)
        monkeypatch.setattr(
            auth_service, "generate_password_reset_token", mock_generate_token
        )

        response = client.post(
            "/api/auth/password_reset_request", json={"email": messages.TEST_USER_EMAIL}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == messages.PASSWORD_RESET_SENT
        mock_send_email.assert_called_once_with(messages.TEST_USER_EMAIL, token, ANY)

    @pytest.mark.asyncio
    async def test_password_reset_request_user_not_found(
        self, client, get_token, monkeypatch
    ):
        self.setup_monkeypatch(monkeypatch)
        mock_send_email = Mock()
        monkeypatch.setattr(
            "src.routes.auth.send_reset_password_email", mock_send_email
        )

        response = client.post(
            "/api/auth/password_reset_request",
            json={"email": "non_existent@example.com"},
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.USER_NOT_FOUND
        mock_send_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_reset_password_confirm_success(self, client, get_token, monkeypatch):
        token = get_token
        new_password = "new_password"
        email = messages.TEST_USER_EMAIL

        mock_verify_token = Mock(return_value=email)
        monkeypatch.setattr(
            auth_service, "verify_password_reset_token", mock_verify_token
        )

        response = client.post(
            f"/api/auth/password_reset/{token}", data={"new_password": new_password}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == messages.PASSWORD_RESET_SUCCESS

        mock_verify_token.assert_called_once_with(token)

    @pytest.mark.asyncio
    async def test_reset_password_confirm_invalid_token(
        elf, client, get_token, monkeypatch
    ):
        token = "invalid_token"
        new_password = "new_password"

        mock_verify_token = Mock(return_value=None)
        monkeypatch.setattr(
            auth_service, "verify_password_reset_token", mock_verify_token
        )

        response = client.post(
            f"/api/auth/password_reset/{token}", data={"new_password": new_password}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == messages.INVALID_TOKEN

        mock_verify_token.assert_called_once_with(token)

    @pytest.mark.asyncio
    async def test_reset_password_confirm_user_not_found(
        elf, client, get_token, monkeypatch
    ):
        token = get_token
        new_password = "new_password"
        email = "non_existent@example.com"

        mock_verify_token = Mock(return_value=email)
        monkeypatch.setattr(
            auth_service, "verify_password_reset_token", mock_verify_token
        )

        response = client.post(
            f"/api/auth/password_reset/{token}", data={"new_password": new_password}
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == messages.USER_NOT_FOUND

        mock_verify_token.assert_called_once_with(token)

    @pytest.mark.asyncio
    async def test_password_reset_form_success(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        response = client.get(f"/api/auth/password_reset/{token}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert token in response.text
