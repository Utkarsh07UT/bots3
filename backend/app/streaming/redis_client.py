import os
import redis
from dotenv import load_dotenv

load_dotenv()

def get_redis_client():
    return redis.from_url(
        os.getenv("REDIS_URL", f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/{os.getenv('REDIS_DB', 0)}"),
        decode_responses=True,
        socket_timeout=10,
        socket_connect_timeout=10,
        socket_keepalive=True,
        retry_on_timeout=True,
    )