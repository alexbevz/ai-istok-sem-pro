from src.scheme import BaseScheme
from typing import Optional

class DataCollectionScheme(BaseScheme):
    user_id: int
    name: str
    qdrant_table_name: str

class CollectionItemScheme(BaseScheme):
    data_collection_id: int
    content: str
    user_content_id: Optional[str] = None

class TextItemScheme(BaseScheme):
    content: str
    user_content_id: Optional[str] = None

class TextProximityItemScheme(BaseScheme):
    content: str
    semantic_proximity: float
    user_content_id: Optional[str] = None

class FindProximityRequest(BaseScheme):
    content: str
    compared_items: list[TextItemScheme]

class FindProximityResponse(BaseScheme):
    content: str
    compared_items_result: list[TextProximityItemScheme]

class DataCollectionRequest(BaseScheme):
    name: str

class DataCollectionResponse(BaseScheme):
    id: int
    name: str

class CreateItemResponse(BaseScheme):
    id: int
    data_collection_id: int
    content: str
    user_content_id: Optional[str] = None

