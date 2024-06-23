import pickle
from datetime import datetime, timedelta
from typing import Optional

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        The verify_password function takes a plain-text password and a hashed password,
            and returns True if the passwords match, False otherwise.


        :param self: Represent the instance of the class
        :param plain_password: str: Pass in the password that is being verified
        :param hashed_password: str: Pass in the hashed password from the database
        :return: A boolean value
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
            The function uses the pwd_context object to generate a hash from the given password.

        :param self: Represent the instance of the class
        :param password: str: Create a password hash
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    async def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): The data to be encoded in the JWT.
                expires_delta (Optional[timedelta]): A timedelta object representing the time until expiration of the token. Defaults to 15 minutes if not provided.

        :param self: Represent the instance of the class
        :param data: dict: Pass the data that you want to encode in your token
        :param expires_delta: Optional[timedelta]: Set the expiration time of the token
        :return: A string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta if expires_delta else timedelta(minutes=15)
        )
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token


    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It uses the OAuth2 token to retrieve and validate
            the user, and assign them to `current_user`.

        :param self: Represent the instance of a class
        :param token: str: Pass the token to the function
        :param db: AsyncSession: Get the database connection
        :return: A user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user_hash = str(email)

        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    async def get_current_active_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        Get the current active user based on the access token.

        :param self: Represent the instance of a class
        :param token: str: Pass the token to the function
        :param db: AsyncSession: Get the database connection
        :return: A user object
        """
        user = await self.get_current_user(token, db)
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not active user")
        return user

    async def get_current_active_user_with_role(
            self, required_role: str, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        Get the current active user based on the access token and check their role.

        :param self: Represent the instance of a class
        :param required_role: str: Required role for access
        :param token: str: Pass the token to the function
        :param db: AsyncSession: Get the database connection
        :return: A user object
        """

        user = await self.get_current_active_user(token, db)
        if user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user

    def create_email_token(self, data: dict):
        """
        The create_email_token function takes a dictionary of data and returns a JWT token.
            The token is encoded with the SECRET_KEY and ALGORITHM defined in the class.
            The expiration date is set to 1 day from now.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the email address of the user
        :return: A token
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=1)
        to_encode.update({"iat": datetime.now(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function uses the jwt library to decode the token, which is then used to retrieve the email address from within it.

        :param self: Represent the instance of the class
        :param token: str: Pass in the token that is sent to the user's email
        :return: The email address of the user who has requested to reset their password
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

    def generate_password_reset_token(self, email: str) -> str:
        """
        The generate_password_reset_token function generates a JWT token that expires in 1 hour.
        The payload contains the email of the user who requested to reset their password.

        :param self: Represent the instance of the class
        :param email: str: Specify the email of the user who is requesting a password reset
        :return: A jwt token
        """
        expire = datetime.now() + timedelta(hours=1)
        payload = {"exp": expire, "email": email}
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """
        The verify_password_reset_token function takes a token as an argument and returns the email address associated with that token.
        If the token is invalid, it raises an HTTPException.

        :param self: Represent the instance of a class
        :param token: str: Pass the token to the function
        :return: The email of the user who requested a password reset
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload["email"]
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )


auth_service = Auth()


def auth_decorator(required_role: str):
    def decorator(func):
        async def role_permissions(username: str, db: AsyncSession = Depends(get_db), token: str = Depends(auth_service.oauth2_scheme)):
            user = await auth_service.get_current_active_user_with_role(
                required_role, token, db
            )
            return await func(username, db, token)
        return role_permissions
    return decorator