from redis_om import get_redis_connection
from config.env import Settings


redis_db = get_redis_connection(
    url=Settings().redis_url,
    encoding=Settings().encoding,
    decode_responses=True
)
