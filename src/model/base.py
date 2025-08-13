import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import TIMESTAMP
from sqlalchemy import Integer
from sqlalchemy import Column


class BaseModel(DeclarativeBase):
    __abstract__ = True
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def update(self, changes: dict):
        for key, value in changes.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id!r})>'
