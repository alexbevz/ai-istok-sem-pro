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
    """Какой коллекции принадлежит элемент"""
    content: str
    """Содержимое элемента"""
    user_content_id: Optional[str] = None
    """ID элемента пользователя"""

class ModelCollectionItemScheme(BaseCollectionItemScheme):
    id: int
    """ID Элемента коллекции"""

class TextItemScheme(BaseScheme):
    content: str
    """Текст элемента"""
    user_content_id: Optional[str] = None
    """ID элемента пользователя кастомный"""

class TextProximityItemScheme(TextItemScheme):
    semantic_proximity: float
    """Точность сравнения"""

class ProximityItemsScheme(BaseScheme):
    content: str
    user_content_id: Optional[str] = None
    compared_items: list[TextItemScheme]

class ProximityResultScheme(BaseScheme):
    content: str
    user_content_id: Optional[str] = None
    compared_items_result: list[TextProximityItemScheme]

class GetProximeItemsScheme(BaseScheme):
    count: int = 5
    limit_accuracy: float = 0.5

class SaveProximeItemsScheme(GetProximeItemsScheme):
    save: bool = False

class CreateDataCollectionScheme(BaseScheme):
    name: str

class UpdateDataCollectionScheme(CreateDataCollectionScheme):
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