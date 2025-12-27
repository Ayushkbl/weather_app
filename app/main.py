from fastapi import FastAPI
from app.routers import weather

app = FastAPI()

app.include_router(weather.router)