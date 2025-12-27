from fastapi import FastAPI
from app.routers import weather
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter

from app.core.redis import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(redis_client)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(weather.router)