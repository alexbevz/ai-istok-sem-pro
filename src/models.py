from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  Column, Integer, String


class Base(DeclarativeBase):
    pass


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    qdrant_collection_name = Column(String)


class CollectionItem(Base):
    __tablename__ = "collection_items"

    id = Column(Integer, primary_key=True, index=True)

