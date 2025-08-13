from src.scheme import BaseScheme
from typing import Optional

class EmbeddingScheme(BaseScheme):
    """Схема эмбеддинга"""
    vector: list[float]

class BaseDataCollectionScheme(BaseScheme):
    """Базовая схема коллекции"""
    user_id: int                                # ID пользователя
    name: str                                   # Имя коллекции
    qdrant_table_name: str                      # Имя таблицы в qdrant

class ModelDataCollectionScheme(BaseDataCollectionScheme):
    """Схема модели коллекции"""
    id: int                                     # ID коллекции

class BaseCollectionItemScheme(BaseScheme):
    """Базовая схема элемента коллекции"""
    data_collection_id: int                     # ID коллекции, в которой находится элемент
    content: str                                # Текст элемента
    user_content_id: Optional[str] = None       # Пользовательский ID

class ModelCollectionItemScheme(BaseCollectionItemScheme):
    """Схема модели элемента коллекции"""
    id: int                                     # ID Элемента коллекции

class TextItemScheme(BaseScheme):
    """Схема текстового элемента"""
    content: str                                # Текст элемента
    user_content_id: Optional[str] = None       # Пользовательский ID

class TextProximityItemScheme(TextItemScheme):
    """Схема элемента со значением близости"""
    semantic_proximity: float                   # Точность сравнения

class ProximityItemsScheme(BaseScheme):
    """Сравниваемый элемент и список для сравнения"""
    content: str                                # Содержимое элемента
    user_content_id: Optional[str] = None       # Пользовательский ID
    compared_items: list[TextItemScheme]        # Список элементов для сравнения

class ProximityResultScheme(BaseScheme):
    """Сравниваемый элемент и результаты сравнения"""
    content: str                                            # Содержимое элемента
    user_content_id: Optional[str] = None                   # Пользовательский ID
    compared_items_result: list[TextProximityItemScheme]    # Список элементов вместе с близостью

class GetProximeItemsScheme(BaseScheme):
    """Настройки получения результатов сравнения"""
    count: int = 5                              # Количество выводимых элементов
    limit_accuracy: float = 0.5                 # Предел точности

class SaveProximeItemsScheme(GetProximeItemsScheme):
    """Сохранение сравниваемого элемента в коллецию"""
    save: bool = False                          # Флаг для сохранения

class CreateDataCollectionScheme(BaseScheme):
    """Схема для создания коллекции"""
    name: str                                   # Имя коллекции

class UpdateDataCollectionScheme(CreateDataCollectionScheme):
    """Схема для редактирования коллекции"""
    pass

class GetDataCollectionScheme(BaseScheme):
    """Схема для получения коллекции по id"""
    id: int                                     # ID коллекции
    name: str                                   # Имя коллекции

class GetAllCollectionElementsScheme(BaseScheme):
    """Схема всех элементов коллекции с пагинацией"""
    result: list[ModelCollectionItemScheme]     # Список полученных элементов
    offset: int                                 # Отступ
    limit: int                                  # Лимит
    total: int                                  # Количество полученных элементов

class NumberOfCreatedItemsScheme(BaseScheme):
    """Количество добавленных элементов"""
    total: int                                  # Количество элементов