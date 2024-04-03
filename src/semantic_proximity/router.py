from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session_db

from src.auth.dependency import get_current_user
from src.auth.model import User

from src.semantic_proximity.service import proximityServ, collectionServ
from src.semantic_proximity.scheme import (ProximityRequestScheme,
                                           EditDataCollectionScheme,
                                           TextItemScheme,
                                           CreateDataCollectionScheme)


from fastapi import File, UploadFile

class SemanticProximityRouter(APIRouter):

    def __init__(self):
        super().__init__(prefix='/sps', tags=['Семантическая близость'])
        self.add_api_route(endpoint=self.find_proximity, path="/find", methods=['GET'])

        self.add_api_route(endpoint=self.create_collection, path="/collections", methods=['POST'])
        self.add_api_route(endpoint=self.get_all_collections, path="/collections", methods=['GET'])
        self.add_api_route(endpoint=self.get_collection, path="/collections/{collection_id}", methods=['GET'])
        self.add_api_route(endpoint=self.edit_collection, path="/collections/{collection_id}", methods=['PUT'])
        self.add_api_route(endpoint=self.delete_collection, path="/collections/{collection_id}", methods=['DELETE'])

        self.add_api_route(endpoint=self.add_collection_item, path="/collections/{collection_id}/items", methods=['POST'])
        self.add_api_route(endpoint=self.add_all_collection_items, path="/collections/{collection_id}/items/batch", methods=['POST'])
        self.add_api_route(endpoint=self.add_items_from_file, path="/collections/{collection_id}/items/file", methods=['POST'])

        self.add_api_route(endpoint=self.get_all_collection_items, path="/collections/{collection_id}/items", methods=['GET'])
        self.add_api_route(endpoint=self.get_collection_item_by_id, path="/collections/{collection_id}/items/{item_id}", methods=['GET'])
        self.add_api_route(endpoint=self.get_collection_item_by_user_content_id, path='/collections/{collection_id}/items/content/{user_content_id}', methods=['GET'])

        self.add_api_route(endpoint=self.edit_collection_item_by_id, path="/collections/{collection_id}/items/{item_id}", methods=['PUT'])
        self.add_api_route(endpoint=self.edit_collection_item_by_user_content_id, path="/collections/{collection_id}/items/content/{user_content_id}", methods=['PUT'])

        self.add_api_route(endpoint=self.delete_collection_item, path="/collections/{collection_id}/items/{item_id}", methods=['DELETE'])

        self.add_api_route(endpoint=self.find_proxime_items, path="/collections/{collection_id}/find", methods=['GET'])
        self.add_api_route(endpoint=self.find_proxime_items_by_id, path="/collections/{collection_id}/items/{item_id}/find", methods=['GET'])
        self.add_api_route(endpoint=self.find_proxime_items_by_user_content_id, path="/collections/{collection_id}/items/content/{user_content_id}/find", methods=['GET'])


    @classmethod
    async def add_items_from_file(cls,
                                  collection_id: int,
                                  file: UploadFile,
                                  separator: str = ',',
                                  user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_session_db)):
        """Добавление элементов коллекции из файла

        Args:
            collection_id (int): id коллекции
            file (UploadFile): Файл для добавления в коллекцию
            separator (str, optional): Разделитель для csv-файлов Defaults to ','.
            user (User, optional): Пользователь к добавляющий колекцию. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            list[ModelCollectionItemScheme]: Список добавленных элементов коллекции
        """
        collection_items = await collectionServ.add_collection_items_from_file(collection_id, file, separator, user, db)
        return collection_items


    @classmethod
    async def find_proximity(cls, proximity_request_scheme: ProximityRequestScheme):
        """Найти семантическую близость

        Args:
            proximity_request_scheme (ProximityRequestScheme): Схема для поиска семантической близости

        Returns:
            ProximityResponseScheme: Схема с результатом поиска
        """
        proximity_response = await proximityServ.find_proximity(proximity_request_scheme)
        return proximity_response

    @classmethod
    async def create_collection(cls,
                                create_collection_scheme: CreateDataCollectionScheme,
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_session_db)):
        """Создание коллекции

        Args:
            create_collection_scheme (CreateDataCollectionScheme): Схема коллекции для создания.
            user (User, optional): получение текущей пользователь. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            GetDataCollectionScheme: Схема созданной коллекции
        """
        collection = await collectionServ.create_collection(create_collection_scheme, user, db)
        return collection
    
    @classmethod
    async def get_all_collections(cls,
                                  user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_session_db)):
        """Получение всех коллекций пользователя

        Args:
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            list[GetDataCollectionScheme]: Список коллекций пользователя
        """
        collections = await collectionServ.get_user_collections(user, db)
        return collections

    @classmethod
    async def get_collection(cls,
                             collection_id: int,
                             user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_session_db)):
        """Получение коллекции по id

        Args:
            collection_id (int): id коллекции
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            GetDataCollectionScheme: Схема коллекции
        """
        collection = await collectionServ.get_collection_by_id(collection_id, user, db)
        return collection

    @classmethod
    async def edit_collection(cls,
                              collection_id: int,
                              edit_collection_scheme: EditDataCollectionScheme,
                              user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_session_db)):
        """Изменение коллекции

        Args:
            collection_id (int): ID коллекции
            edit_collection_scheme (EditDataCollectionScheme): Схема для изменения коллекции
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            GetDataCollectionScheme: Измененная коллекция
        """
        collection = await collectionServ.edit_collection_by_id(collection_id, edit_collection_scheme, user, db)
        return collection

    @classmethod
    async def delete_collection(cls,
                                collection_id: int,
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_session_db)):
        """Удаление коллекции

        Args:
            collection_id (int): ID коллекции
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            GetDataCollectionScheme: удаленная коллекция
        """
        collection = await collectionServ.delete_collection_by_id(collection_id, user, db)
        return collection


    @classmethod
    async def add_collection_item(cls,
                                  collection_id: int,
                                  add_collection_item_scheme: TextItemScheme,
                                  user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_session_db)):
        """Добавление элемента в коллекцию

        Args:
            collection_id (int): ID коллекции
            add_collection_item_scheme (TextItemScheme): Элемент для добавления
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ModelCollectionItemScheme: добавленный элемент
        """
        collection_item = await collectionServ.add_collection_item(collection_id, add_collection_item_scheme, user, db)
        return collection_item
    
    @classmethod
    async def add_all_collection_items(cls,
                                       collection_id: int,
                                       add_collection_items_scheme: list[TextItemScheme],
                                       user: User = Depends(get_current_user),
                                       db: AsyncSession = Depends(get_session_db)):
        """Добавление элементов в коллекцию

        Args:
            collection_id (int): ID коллекции
            add_collection_items_scheme (list[TextItemScheme]): Список элементов для добавления
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            list[ModelCollectionItemScheme]: список добавленных элементов
        """
        collection_items = await collectionServ.add_collection_items(collection_id, add_collection_items_scheme, user, db)
        return collection_items


    @classmethod
    async def get_all_collection_items(cls,
                                       collection_id: int,
                                       offset = 0,
                                       limit = 10,
                                       user: User = Depends(get_current_user),
                                       db: AsyncSession = Depends(get_session_db)):
        """Получение всех элементов коллекций

        Args:
            collection_id (int): ID коллекции
            offset (int, optional): С какого индекса. Defaults to 0.
            limit (int, optional): По какой индекс. Defaults to 10.
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            GetAllCollectionElementsScheme: схема элементов
        """
        collection_items = await collectionServ.get_all_collection_items(collection_id, offset, limit, user, db)
        return collection_items
    
    @classmethod
    async def get_collection_item_by_id(cls,
                                        collection_id: int,
                                        item_id: int,
                                        user: User = Depends(get_current_user),
                                        db: AsyncSession = Depends(get_session_db)):
        """Получение элемента из коллекии

        Args:
            collection_id (int): ID коллекции
            item_id (int): ID элемента
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ModelDataCollectionScheme: элемент из коллекции
        """
        collection_item = await collectionServ.get_collection_item_by_id(collection_id, item_id, user, db)
        return collection_item
    
    @classmethod
    async def get_collection_item_by_user_content_id(cls,
                                                     collection_id: int,
                                                     user_content_id: int,
                                                     user: User = Depends(get_current_user),
                                                     db: AsyncSession = Depends(get_session_db)):
        """Получение коллекций пользователя

        Args:
            collection_id (int): ID коллекции
            user_content_id (int): ID контента
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ModelCollectionItemScheme: элемент из коллекции
        """
        collection_item = await collectionServ.get_collection_item_by_user_content_id(collection_id, user_content_id, user, db)
        return collection_item
    
    @classmethod
    async def edit_collection_item_by_id(cls,
                                         collection_id: int,
                                         item_id: int,
                                         edit_collection_item_scheme: TextItemScheme,
                                         user: User = Depends(get_current_user),
                                         db: AsyncSession = Depends(get_session_db)):
        """Изменение элемента коллекции

        Args:
            collection_id (int): ID коллекции
            item_id (int): ID элемента
            edit_collection_item_scheme (TextItemScheme): Измененный элемент
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ModelDataCollectionScheme: Измененный элемент
        """
        collection_item = await collectionServ.edit_collection_item_by_id(collection_id, item_id, edit_collection_item_scheme, user, db)
        return collection_item

    @classmethod
    async def edit_collection_item_by_user_content_id(cls,
                                         collection_id: int,
                                         user_content_id: int,
                                         edit_collection_item_scheme: TextItemScheme,
                                         user: User = Depends(get_current_user),
                                         db: AsyncSession = Depends(get_session_db)):
        """Изменение элемента коллекции

        Args:
            collection_id (int): ID коллекции
            user_content_id (int): ID пользовательского контента
            edit_collection_item_scheme (TextItemScheme): Измененный элемент
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ModelDataCollectionScheme: Изменённый элемент
        """
        collection_item = await collectionServ.edit_collection_item_by_user_content_id(collection_id, user_content_id, edit_collection_item_scheme, user, db)
        return collection_item
    
    @classmethod
    async def delete_collection_item(cls,
                                     collection_id: int,
                                     item_id: int,
                                     user: User = Depends(get_current_user),
                                     db: AsyncSession = Depends(get_session_db)):
        """Удаление элемента коллекции

        Args:
            collection_id (int): ID коллекции
            item_id (int): ID элемента
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ModelCollectionItemScheme: Удаленный элемент
        """
        collection_item = await collectionServ.delete_collection_item(collection_id, item_id, user, db)
        return collection_item
    
    @classmethod
    async def find_proxime_items(cls,
                                 collection_id: int,
                                 find_proxime_items_scheme: TextItemScheme,
                                 save: bool=False,
                                 count: int=-1,
                                 limit_accuracy: float=0.1,
                                 user: User = Depends(get_current_user),
                                 db: AsyncSession = Depends(get_session_db)):
        """Поиск семантически близких элементов

        Args:
            collection_id (int): ID коллекции
            find_proxime_items_scheme (TextItemScheme): Схема для поиска
            save (bool, optional): Добавлять в коллекцию. Defaults to False.
            count (int, optional): Количество выводимых элементов. Defaults to -1.
            limit_accuracy (float, optional): Предел точности. Defaults to 0.1.
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ProximityResponseScheme: Схема с результатом поиска
        """
        collection_items = await collectionServ.find_proxime_items(collection_id, find_proxime_items_scheme, save, count, limit_accuracy, user, db)
        return collection_items

    @classmethod
    async def find_proxime_items_by_id(cls,
                                       collection_id: int,
                                       item_id: int,
                                       count: int=-1,
                                       limit_accuracy: float=0.1,
                                       user: User = Depends(get_current_user),
                                       db: AsyncSession = Depends(get_session_db)):
        """Поиск семантически близких элементов по ID

        Args:
            collection_id (int): ID коллекции
            item_id (int): ID элемента
            count (int, optional): Количество. Defaults to -1.
            limit_accuracy (float, optional): Предел точности. Defaults to 0.1.
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ProximityResponseScheme: Схема с результатом поиска
        """
        collection_items = await collectionServ.find_proxime_items_by_id(collection_id, item_id, count, limit_accuracy, user, db)
        return collection_items

    @classmethod
    async def find_proxime_items_by_user_content_id(cls,
                                                    collection_id: int,
                                                    user_content_id: int,
                                                    count: int=-1,
                                                    limit_accuracy: float=0.1,
                                                    user: User = Depends(get_current_user),
                                                    db: AsyncSession = Depends(get_session_db)):
        """Поиск семантически близких элементов по ID контента

        Args:
            collection_id (int): ID коллекции
            user_content_id (int): ID контента
            count (int, optional): Количество. Defaults to -1.
            limit_accuracy (float, optional): Предел точности. Defaults to 0.1.
            user (User, optional): Получение текущего пользователя. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): Получение сессии. Defaults to Depends(get_session_db).

        Returns:
            ProximityResponseScheme: Схема с результатом поиска
        """
        collection_items = await collectionServ.find_proxime_items_by_user_content_id(collection_id, user_content_id, count, limit_accuracy, user, db)
        return collection_items

spsRouter = SemanticProximityRouter()

