import os
from urllib.parse import quote


class DatabaseConfig:
    """
    FIXME: вынести метод экранирования отдельно
    """
    db_driver = os.getenv('DB_DRIVER', 'postgresql')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = quote(os.getenv('DB_PASSWORD', 'postgres'))
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_database_name = os.getenv('DB_DATABASE_NAME', 'ai-finder')

    @classmethod
    def get_url(cls, sync: bool = False) -> str:
        extra_args = '' if sync else '+asyncpg'
        return (f'{cls.db_driver}{extra_args}://'f'{cls.db_user}:{cls.db_password}@'
                f'{cls.db_host}:{cls.db_port}/{cls.db_database_name}')

    @classmethod
    def get_alembic_url(cls) -> str:
        return (f'{cls.db_driver}://'f'{cls.db_user}:{cls.db_password.replace("%", "%%")}@'
                f'{cls.db_host}:{cls.db_port}/{cls.db_database_name}')
