import os


class DatabaseConfig:
    db_driver = os.getenv('DB_DRIVER', 'postgresql')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_database_name = os.getenv('DB_DATABASE_NAME', 'ai-finder')

    def get_url(self):
        return (f'{self.db_driver}://'f'{self.db_user}:{self.db_password}@'
                f'{self.db_host}:{self.db_port}/{self.db_database_name}')
