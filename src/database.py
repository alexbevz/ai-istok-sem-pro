from config import DatabaseConfig

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


db_config = DatabaseConfig()

db_engine = create_engine(url=db_config.get_url(), echo=False)

db_session_factory = sessionmaker(bind=db_engine)


def get_session_db():
    return db_session_factory()
