from src.scheme import BaseScheme
from typing import Optional

class BaseDataCollectionScheme(BaseScheme):
    user_id: int
    name: str
    qdrant_table_name: str

class ModelDataCollectionScheme(BaseDataCollectionScheme):
    id: int

class BaseCollectionItemScheme(BaseScheme):
    data_collection_id: int
    content: str
    user_content_id: Optional[str] = None

class ModelCollectionItemScheme(BaseCollectionItemScheme):
    id: int

class TextItemScheme(BaseScheme):
    content: str
    user_content_id: Optional[str] = None

class TextProximityItemScheme(TextItemScheme):
    semantic_proximity: float

class ProximityRequestScheme(BaseScheme):
    content: str
    user_content_id: Optional[str] = None
    compared_items: list[TextItemScheme]

class ProximityResponseScheme(BaseScheme):
    content: str
    user_content_id: Optional[str] = None
    compared_items_result: list[TextProximityItemScheme]

class CreateDataCollectionScheme(BaseScheme):
    name: str

class EditDataCollectionScheme(CreateDataCollectionScheme):
    pass

class GetDataCollectionScheme(BaseScheme):
    id: int
    name: str

class CreateItemResponseScheme(ModelCollectionItemScheme):
    pass

class GetAllCollectionElementsScheme(BaseScheme):
    result: list[ModelCollectionItemScheme]
    offset: int
    limit: int
    total: int

class NumberOfCreatedItemsScheme(BaseScheme):
    total: int