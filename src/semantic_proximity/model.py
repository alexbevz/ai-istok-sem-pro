from sqlalchemy import Column, Integer, ForeignKey, String

from src.model.base import BaseModel
from src.auth.model import User

class DataCollection(BaseModel):
    __tablename__ = 'data_collection'

    user_id = Column(Integer,
                     ForeignKey(User.__tablename__),
                     nullable=False)

    name = Column(String(),
                  nullable=False)
    
    qdrant_table_name = Column(String(),
                               nullable=False,
                               unique=True)
    
    def __repr__(self):
        return f'DataCollection(id={self.id!r}, name={self.name!r}, qdrant_table_name={self.qdrant_table_name!r})'

class CollectionItem(BaseModel):
    __tablename__ = 'collection_item'

    data_collection_id = Column(Integer,
                                ForeignKey(DataCollection.__tablename__),
                                nullable=False)
    
    content = Column(String(),
                     nullable=False)
    
    user_content_id = Column(String(),
                             nullable=True)
    
    def __repr__(self):
        return f'CollectionItem(id={self.id!r}, data_collection_id={self.data_collection_id!r}, content={self.content!r}, user_content_id={self.user_content_id!r})'