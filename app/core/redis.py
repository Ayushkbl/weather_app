from pathlib import Path
from dotenv import load_dotenv
from redis.asyncio import Redis
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)
dotenv_path = BASE_DIR / '.env'
print(dotenv_path)
load_dotenv(dotenv_path=dotenv_path)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)