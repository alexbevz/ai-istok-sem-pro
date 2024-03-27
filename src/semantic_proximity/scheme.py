from src.scheme import BaseScheme
from typing import Optional

class BaseDataCollectionScheme(BaseScheme):
    user_id: int
    """ID пользователя"""
    name: str
    """Имя коллекции"""
    qdrant_table_name: str
    """Имя таблицы в qdrant"""

class ModelDataCollectionScheme(BaseDataCollectionScheme):
    id: int
    """ID коллекции"""

class BaseCollectionItemScheme(BaseScheme):
    data_collection_id: int
    """Какокой коллекции прингадлежит элемент"""
    content: str
    """Содержимое элемента"""
    user_content_id: Optional[str] = None
    """ID элемента пользователя"""

class ModelCollectionItemScheme(BaseCollectionItemScheme):
    id: int
    """Id полученный postgre"""

class TextItemScheme(BaseScheme):
    content: str
    """Текст элемента"""
    user_content_id: Optional[str] = None
    """ID элемента пользователя кастомный"""

class TextProximityItemScheme(TextItemScheme):
    semantic_proximity: float
    """Точность сравнения"""

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