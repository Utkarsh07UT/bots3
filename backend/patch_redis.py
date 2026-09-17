import re
with open("backend/app/streaming/redis_client.py", "r") as f:
    content = f.read()

content = content.replace(
    'os.getenv("REDIS_URL"),',
    'os.getenv("REDIS_URL", f"redis://{os.getenv(\'REDIS_HOST\', \'localhost\')}:{os.getenv(\'REDIS_PORT\', 6379)}/{os.getenv(\'REDIS_DB\', 0)}"),'
)

with open("backend/app/streaming/redis_client.py", "w") as f:
    f.write(content)
