from ipaddress import ip_address
from typing import Callable
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from sqlalchemy import text

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import auth, contacts, users
from src.conf.config import config

app = FastAPI()

banned_ips = [
    ip_address("192.168.1.1"),
    ip_address("192.168.1.2"),
]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    ip = ip_address(ip)
    if ip in banned_ips:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
        )
    response = await call_next(request)
    return response


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.on_event("startup")
# TODO: розібратися з новим методом і переробити
async def startup():
    """
    This function is an event handler that runs when the FastAPI application starts up.
    It initializes a Redis connection and passes it to the FastAPILimiter for rate limiting.

    :return: None
    :raises: None

    :doc-author: Trelent
    """
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database connection is working.
    It does this by making a request to the database and checking if it returns any results.
    If there are no results, then we know something went wrong with our connection.

    :param db: AsyncSession: Pass the database session to the function
    :return: A dict
    :doc-author: Trelent
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
