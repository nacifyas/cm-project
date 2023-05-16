from aredis_om import get_redis_connection
from config.settings import Settings


redis = get_redis_connection(
    url=Settings.redis_url,
    encoding=Settings.encoding,
    decode_responses=True
)

print(redis.ping())
