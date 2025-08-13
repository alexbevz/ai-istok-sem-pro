import redis

from src.auth.config import RedisConfig

class RedisConnectionManager:

    def __init__(self, db: int=0):
        self.db = db
        self.redis_conn = redis.Redis(
            host=RedisConfig.get_host(),
            port=RedisConfig.get_port(),
            db=self.db
            )
        self.pipeline = self.redis_conn.pipeline()

    def __enter__(self):
        with redis.Redis(
            host=RedisConfig.get_host(),
            port=RedisConfig.get_port(),
            db=self.db
            ) as redis_conn:
            self.pipeline = redis_conn.pipeline()
            self.pipeline.multi()
            return self.pipeline

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.pipeline.execute()
            self.pipeline.close()
            self.redis_conn.close()
        else:
            self.pipeline.discard()
            raise exc_type(exc_value)
