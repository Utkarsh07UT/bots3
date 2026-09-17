import os
import redis
from dotenv import load_dotenv

load_dotenv()

# redis_client.py
def get_redis_client():
    return redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)