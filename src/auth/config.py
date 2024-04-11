import os

class RedisConfig:
    _host = os.getenv('DB_REDIS', 'localhost')
    _port = int(os.getenv('REDIS_PORT', 6379))

    @classmethod
    def get_host(cls) -> str:
        return cls._host

    @classmethod
    def get_port(cls) -> int:
        return cls._port

class JwtConfig:
    _secret_key = os.getenv('JWT_SECRET_KEY', '3dcbe5ddffe500ffa2e7b4d427899349cbdf491bddef3b3611a328b966eb874d')
    _algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
    _expire_minutes = int(os.getenv('JWT_EXPIRE_MINUTES', 5))
    _ttl_access = int(os.getenv('JWT_TTL_ACCESS', 5))
    _ttl_refresh = int(os.getenv('JWT_TTL_REFRESH', 60 * 24))

    @classmethod
    def get_secret_key(cls) -> str:
        return cls._secret_key

    @classmethod
    def get_algorithm(cls) -> str:
        return cls._algorithm

    @classmethod
    def get_expire_minutes(cls) -> int:
        return cls._expire_minutes

    @classmethod
    def get_ttl_access(cls) -> int:
        return cls._ttl_access

    @classmethod
    def get_ttl_refresh(cls) -> int:
        return cls._ttl_refresh
