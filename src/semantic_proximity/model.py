from sqlalchemy import Column, Integer, ForeignKey, String

from src.model.base import BaseModel
from src.auth.model import User

class DataCollection(BaseModel):
    user_id = Column(Integer,
                     ForeignKey(User.__tablename__),
                     nullable=False)

    name = Column(String(),
                  nullable=False)
    
    qdrant_table_name = Column(String(),
                               nullable=False)

class CollectionItem(BaseModel):
    data_collection_id = Column(Integer,
                                ForeignKey(DataCollection.__tablename__),
                                nullable=False)
    
    content = Column(String(),
                     nullable=False)
    
    user_content_id = Column(String(),
                             nullable=True)