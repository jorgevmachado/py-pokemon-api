import redis.asyncio as redis

from app.core.settings import Settings

redis_client = redis.Redis(
    host=Settings().REDIS_HOST,
    port=Settings().REDIS_PORT,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
)
