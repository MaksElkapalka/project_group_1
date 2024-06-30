# import unittest
# from unittest.mock import AsyncMock, MagicMock, patch
# from fastapi import BackgroundTasks, Request, HTTPException
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
# from src.routes.users import router
# from src.schemas.user import UserSchema
# from src.repository import users as repositories_users
# from src.services.auth import auth_service


# class TestSignupEndpoint(unittest.IsolatedAsyncioTestCase):
#     def setUp(self):
#         self.session = MagicMock(spec=AsyncSession)
#         self.user_data = {
#             "username": "testuser",
#             "email": "test@example.com",
#             "password": "12345678",
#         }

#     @patch("src.services.auth.auth_service", spec=True)
#     async def test_signup_endpoint(self, mock_create_user):
#         async with AsyncClient(app=router) as client:
#             mock_request = MagicMock(spec=Request)
#             mock_request.base_url = "http://testserver"

#         self.session.add = AsyncMock()
#         self.session.commit = AsyncMock()

#         mock_background_tasks = MagicMock(spec=BackgroundTasks)
#         mock_background_tasks.add_task = MagicMock()

#         user_schema = UserSchema(**self.user_data)

#         mock_create_user.return_value = user_schema
#         repositories_users.get_user_by_email = AsyncMock(return_value=None)

#         response = await client.post(
#             "/auth/signup",
#             json=self.user_data,
#             bt=mock_background_tasks,
#             request=mock_request,
#             db=self.session,
#         )

#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(
#             response.json(),
#             {
#                 "username": "testuser",
#                 "email": "test@example.com",
#             },
#         )

#         mock_background_tasks.add_task.assert_called_once()
#         mock_create_user.assert_called_once_with(user_schema, self.session)


# if __name__ == "__main__":
#     unittest.main()
