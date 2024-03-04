class JwtConfig:
    _secret_key = '3dcbe5ddffe500ffa2e7b4d427899349cbdf491bddef3b3611a328b966eb874d'
    _algorithm = 'HS256'
    _expire_minutes = 5
    _ttl_access = 5
    _ttl_refresh = 60 * 24 * 7

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
