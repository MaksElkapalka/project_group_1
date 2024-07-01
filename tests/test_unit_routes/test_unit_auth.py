import unittest
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from main import app
from src.services.auth import auth_service
from src.repository.users import create_user


class TestSignup(unittest.IsolatedAsyncioTestCase):
    user_data = {
        "username": "tes_user_auth",
        "email": "tes_email_auth@example.com",
        "password": "12345678",
    }

    def setUp(self):
        self.client = TestClient(app)

    def setup_monkeypatch(self):
        self.redis_patch = patch.object(auth_service, "cache", new_callable=AsyncMock)
        self.redis_mock = self.redis_patch.start()
        self.redis_mock.get.return_value = None

        self.limiter_redis_patch = patch(
            "fastapi_limiter.FastAPILimiter.redis", AsyncMock()
        )
        self.limiter_redis_mock = self.limiter_redis_patch.start()

        self.limiter_identifier_patch = patch(
            "fastapi_limiter.FastAPILimiter.identifier", AsyncMock()
        )
        self.limiter_identifier_mock = self.limiter_identifier_patch.start()

        self.limiter_http_callback_patch = patch(
            "fastapi_limiter.FastAPILimiter.http_callback", AsyncMock()
        )
        self.limiter_http_callback_mock = self.limiter_http_callback_patch.start()

        self.create_user_patch = patch(
            "src.repository.users.create_user", new_callable=AsyncMock
        )
        self.create_user_mock = self.create_user_patch.start()
        self.create_user_mock.return_value = {
            "username": self.user_data["username"],
            "email": self.user_data["email"],
            "avatar": "avatar_url",
        }

    def tearDown(self):
        self.redis_patch.stop()
        self.limiter_redis_patch.stop()
        self.limiter_identifier_patch.stop()
        self.limiter_http_callback_patch.stop()
        self.create_user_patch.stop()

    async def test_signup(self):
        self.setup_monkeypatch()

        mock_send_email = Mock()
        with patch("src.routes.auth.send_email", mock_send_email):
            with patch(
                "main.ip_address",
                side_effect=lambda x: x if x != "testclient" else "127.0.0.1",
            ):
                response = self.client.post(
                    "/auth/signup", data=self.user_data
                )  # Correct path
                # self.assertEqual(response.status_code, 201)
                data = response
                self.assertEqual(data["username"], self.user_data["username"])
                self.assertEqual(data["email"], self.user_data["email"])
                self.assertNotIn("password", data)
                self.assertIn("avatar", data)


if __name__ == "__main__":
    unittest.main()
