from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.models import PointStruct

from src.auth.model import User
from src.semantic_proximity.util import (EmbeddingUtil,
                                         SimilarityUtil,
                                         CollectionUtil,
                                         FileUtil)

from src.semantic_proximity.model import CollectionItem, DataCollection

from src.semantic_proximity.repository import (collectionRep,
                                               itemRep)

from src.semantic_proximity.scheme import (BaseDataCollectionScheme,
                                           BaseCollectionItemScheme,
                                           ModelDataCollectionScheme,
                                           ModelCollectionItemScheme,
                                           ProximityItemsScheme,
                                           ProximityResultScheme,
                                           TextProximityItemScheme,
                                           CreateDataCollectionScheme,
                                           GetDataCollectionScheme,
                                           UpdateDataCollectionScheme,
                                           TextItemScheme,
                                           GetAllCollectionElementsScheme,
                                           NumberOfCreatedItemsScheme,
                                           GetProximeItemsScheme,
                                           SaveProximeItemsScheme)

from src.semantic_proximity.exception import (CollectionAlreadyExistsException,
                                              WrongCollectionException,
                                              BatchSizeException,
                                              QdrantCollectionException)

from src.scheme import PageScheme

from src.semantic_proximity.vector_repository import vectorRep
from src.semantic_proximity.config import QdrantConfig, FileConfig

class ProximityService:

    @classmethod
    async def find_proximity(cls, proximity_items: ProximityItemsScheme) -> ProximityResultScheme:
        embedding = EmbeddingUtil.calculate_embedding(proximity_items.content)
        compared_items = [item.content for item in proximity_items.compared_items]
        target_embeddings = EmbeddingUtil.calculate_embedding(compared_items)
        distance_metric = SimilarityUtil.choose_distance_metric(QdrantConfig.get_distance_metric())
        similarities = distance_metric(embedding, target_embeddings)
        similarity_items = []
        for content, similarity in zip(compared_items, similarities):
            similarity_items.append(
                TextProximityItemScheme(
                    content=content,
                    semantic_proximity=similarity
                )
            )
        return ProximityResultScheme(
            content=proximity_items.content,
            compared_items_result=similarity_items
        )


proximityServ = ProximityService()

class CollectionService:

    @classmethod
    async def create_collection(cls,
                                create_collection_scheme: CreateDataCollectionScheme,
                                user: User,
                                db: AsyncSession) -> GetDataCollectionScheme:

        qdrant_table_name = CollectionUtil.generate_qdrant_name()
        data_collection_scheme = BaseDataCollectionScheme(
            user_id=user.id,
            name=create_collection_scheme.name,
            qdrant_table_name=qdrant_table_name)
        data_collection_model = DataCollection(**data_collection_scheme.model_dump())
        try:
           vectorRep.create_collection(data_collection_scheme.qdrant_table_name)
        except Exception as e:
            raise QdrantCollectionException(f"Error while creating collection {create_collection_scheme.name}: {e}")
        data_collection = await collectionRep.create(model=data_collection_model,
                                                     session=db)
        return GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)


    @classmethod
    async def get_user_collections(cls,
                                   user: User,
                                   db: AsyncSession) -> list[GetDataCollectionScheme]:

        data_collections = await collectionRep.get_all_by_field(field=DataCollection.user_id,
                                                                     value=user.id,
                                                                     session=db)
        data_collection_schemes = []
        for item in data_collections:
            data_collection_schemes.append(GetDataCollectionScheme.model_validate(item, from_attributes=True))

        return data_collection_schemes

    @classmethod
    async def get_collection_by_id(cls,
                                   collection_id: int,
                                   user: User,
                                   db: AsyncSession) -> GetDataCollectionScheme:

        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        return GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)

    @classmethod
    async def update_collection_by_id(cls,
                                      collection_id: int,
                                      update_collection_scheme: UpdateDataCollectionScheme,
                                      user: User,
                                      db: AsyncSession) -> GetDataCollectionScheme:
        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        data_collection.name = update_collection_scheme.name
        data_collection = await collectionRep.update(model=data_collection, session=db)

        data_collection_scheme = GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)
        return data_collection_scheme

    @classmethod
    async def delete_collection_by_id(cls,
                                      collection_id: int,
                                      user: User,
                                      db: AsyncSession) -> GetDataCollectionScheme:

        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        vectorRep.delete_collection(data_collection.qdrant_table_name)
        data_collection = await collectionRep.delete_by_id(model_id=collection_id, session=db)
        await itemRep.delete_all_by_field(field=CollectionItem.data_collection_id,
                                          value=data_collection.id,
                                          session=db)

        data_collection_scheme = GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)
        return data_collection_scheme

    @classmethod
    async def add_collection_item(cls,
                                  collection_id: int,
                                  add_collection_item_scheme: TextItemScheme,
                                  user: User,
                                  db: AsyncSession) -> ModelCollectionItemScheme:

        items_list = [add_collection_item_scheme,]
        added_items = await cls.add_collection_items(collection_id, items_list, user, db)
        return added_items[0]

    @classmethod
    async def add_collection_items(cls,
                                   collection_id: int,
                                   items_list: list[TextItemScheme],
                                   user: User,
                                   db: AsyncSession) -> list[ModelCollectionItemScheme]:

        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        batch_size = FileConfig.get_batch_size()

        if len(items_list) > batch_size:
            raise BatchSizeException(f"Batch is too big. Max {batch_size} items")

        collection_item_models = []
        for item in items_list:
            collection_item_scheme = BaseCollectionItemScheme(
                data_collection_id=collection_id,
                content=item.content,
                user_content_id=item.user_content_id
            )
            collection_item_models.append(CollectionItem(**collection_item_scheme.model_dump()))

        collection_item_models = await itemRep.create_all(models=collection_item_models,
                                                          session=db)
        collection_items = []
        for collection_item in collection_item_models:
            collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
            collection_items.append(collection_item_scheme)

        points = []
        for collection_item in collection_items:
            vector = EmbeddingUtil.calculate_embedding(collection_item.content)
            payload = {
                "content": collection_item.content
            }
            point = PointStruct(
                id=collection_item.id,
                payload=payload,
                vector=vector
            )
            points.append(point)
        vectorRep.add_points(collection_name=data_collection.qdrant_table_name,
                             points=points)
        return collection_items

    @classmethod
    async def add_collection_items_from_file(cls,
                                             collection_id: int,
                                             file,
                                             separator: str,
                                             user: User,
                                             db: AsyncSession) -> NumberOfCreatedItemsScheme:
        file_handler = FileUtil.get_file_handler(file.filename, separator=separator)
        file_object = file.file
        items = file_handler(file_object)
        batch_size = FileConfig.get_batch_size()
        batches = FileUtil.get_batches(items=items, batch_size=batch_size)
        all_items_list = []
        for batch in batches:
            batch_items_list = []
            for item in batch:
                collection_item_scheme = TextItemScheme(
                    content=item['content'],
                    user_content_id=item['user_content_id']
                )
                batch_items_list.append(collection_item_scheme)
            collection_items = await cls.add_collection_items(collection_id=collection_id,
                                                              items_list=batch_items_list,
                                                              user=user,
                                                              db=db)
            all_items_list.extend(collection_items)

        number_of_created_items = NumberOfCreatedItemsScheme(
            total=len(all_items_list)
        )
        return number_of_created_items

    @classmethod
    async def get_all_collection_items_by_collection_id(cls,
                                                        collection_id: int,
                                                        page: PageScheme,
                                                        user: User,
                                                        db: AsyncSession) -> GetAllCollectionElementsScheme:

        offset = page.offset
        limit = page.limit
        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        collection_items = await itemRep.get_all_by_field(field=CollectionItem.data_collection_id,
                                                          value=data_collection.id,
                                                          session=db)
        collection_items = collection_items[offset:offset+limit]
        collection_items_list = []
        for item in collection_items:
            collection_items_list.append(ModelCollectionItemScheme.model_validate(item, from_attributes=True))
        items_num = len(collection_items_list)
        collection_elements = GetAllCollectionElementsScheme(
            result=collection_items_list,
            offset=offset,
            limit=limit,
            total=items_num
        )
        return collection_elements

    @classmethod
    async def get_collection_item_by_id(cls,
                                        collection_id: int,
                                        item_id: int,
                                        user: User,
                                        db: AsyncSession)->ModelCollectionItemScheme:
        # TODO: дописать метод позже
        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)
        collection_item = await CollectionUtil.get_collection_item(collection_id, item_id, db)

        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item,
                                                                          from_attributes=True)
        return collection_item_scheme

    @classmethod
    async def get_collection_item_by_user_content_id(cls,
                                                     collection_id: int,
                                                     user_content_id: int,
                                                     user: User,
                                                     db: AsyncSession) -> ModelCollectionItemScheme:

        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)
        collection_items = await itemRep.get_all_by_field(field=CollectionItem.user_content_id,
                                                          value=user_content_id,
                                                          session=db)
        collection_item = collection_items[0]
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item,
                                                                            from_attributes=True)
        if collection_item_scheme.data_collection_id != collection_id:
            raise WrongCollectionException(f"Item with id {user_content_id} doesn't belong to collection {collection_id}")
        return collection_item_scheme

    @classmethod
    async def update_collection_item_by_id(cls,
                                           collection_id: int,
                                           item_id: int,
                                           update_collection_item_scheme: TextItemScheme,
                                           user: User,
                                           db: AsyncSession) -> ModelDataCollectionScheme:

        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        collection_item = await CollectionUtil.get_collection_item(collection_id, item_id, db)

        collection_item.content = update_collection_item_scheme.content
        collection_item.user_content_id = update_collection_item_scheme.user_content_id
        collection_item = await itemRep.update(model=collection_item,
                                               session=db)
        collection_name = data_collection.qdrant_table_name
        vector = EmbeddingUtil.calculate_embedding(update_collection_item_scheme.content)
        payload = {
            "content": update_collection_item_scheme.content
        }
        point = PointStruct(
            id=collection_item.id,
            payload=payload,
            vector=vector
        )
        vectorRep.add_point(collection_name=collection_name, point=point)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        return collection_item_scheme

    @classmethod
    async def update_collection_item_by_user_content_id(cls,
                                                        collection_id: int,
                                                        user_content_id: int,
                                                        update_collection_item_scheme: TextItemScheme,
                                                        user: User,
                                                        db: AsyncSession) -> ModelDataCollectionScheme:

        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        collection_items = await itemRep.get_all_by_field(field=CollectionItem.user_content_id,
                                                          value=user_content_id,
                                                          session=db)
        collection_item = collection_items[0]
        item_id = collection_item.id
        return await cls.update_collection_item_by_id(collection_id, item_id, update_collection_item_scheme, user, db)

    @classmethod
    async def delete_collection_item(cls,
                                     collection_id: int,
                                     item_id: int,
                                     user: User,
                                     db: AsyncSession) -> ModelCollectionItemScheme:

        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)
        collection_item = await CollectionUtil.get_collection_item(collection_id, item_id, db)

        collection_item = await itemRep.delete_by_id(model_id=item_id,
                                                     session=db)
        collection_name = data_collection.qdrant_table_name
        vectorRep.delete_point_by_id(collection_name=collection_name, point_id=item_id)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        return collection_item_scheme

    @classmethod
    async def find_proxime_items(cls,
                                 collection_id: int,
                                 find_proxime_items_scheme: TextItemScheme,
                                 save_proxime_items_scheme: SaveProximeItemsScheme,
                                 user: User,
                                 db: AsyncSession) -> ProximityResultScheme:

        count = save_proxime_items_scheme.count
        limit_accuracy = save_proxime_items_scheme.limit_accuracy
        save = save_proxime_items_scheme.save
        data_collection = await CollectionUtil.get_collection(collection_id, db)
        await CollectionUtil.check_collection_owner(data_collection, user)

        vector = EmbeddingUtil.calculate_embedding(find_proxime_items_scheme.content)
        nearest = vectorRep.find_nearest_by_vector(collection_name=data_collection.qdrant_table_name,
                                                   limit=count+1,
                                                   vector=vector)
        filtered_result = []
        for item in nearest:
            if item.score >= limit_accuracy:
                proximity_item = TextProximityItemScheme(
                    content=item.payload["content"],
                    semantic_proximity=item.score
                )
                filtered_result.append(proximity_item)
        filtered_result = filtered_result[:count]
        if save:
            await cls.add_collection_item(collection_id, find_proxime_items_scheme, user, db)

        proximity_result_scheme = ProximityResultScheme(
            content=find_proxime_items_scheme.content,
            user_content_id=find_proxime_items_scheme.user_content_id,
            compared_items_result=filtered_result
        )
        return proximity_result_scheme

    @classmethod
    async def find_proxime_items_by_id(cls,
                                       collection_id: int,
                                       item_id: int,
                                       get_proxime_items_scheme: GetProximeItemsScheme,
                                       user: User,
                                       db: AsyncSession) -> ProximityResultScheme:

        collection_item = await cls.get_collection_item_by_id(
            collection_id=collection_id,
            item_id=item_id,
            user=user,
            db=db
        )
        save_proxime_items_scheme = SaveProximeItemsScheme(
            count=get_proxime_items_scheme.count,
            limit_accuracy=get_proxime_items_scheme.limit_accuracy,
            save=False
        )
        collection_item_scheme = TextItemScheme(
            content=collection_item.content,
            user_content_id=collection_item.user_content_id
        )
        proximity_result_scheme = await cls.find_proxime_items(
            collection_id=collection_id,
            find_proxime_items_scheme=collection_item_scheme,
            save_proxime_items_scheme=save_proxime_items_scheme,
            user=user,
            db=db
        )
        return proximity_result_scheme

    @classmethod
    async def find_proxime_items_by_user_content_id(cls,
                                                    collection_id: int,
                                                    user_content_id: int,
                                                    get_proxime_items_scheme: GetProximeItemsScheme,
                                                    user: User,
                                                    db: AsyncSession) -> ProximityResultScheme:

        collection_item = await cls.get_collection_item_by_user_content_id(
            collection_id=collection_id,
            user_content_id=user_content_id,
            user=user,
            db=db
        )
        save_proxime_items_scheme = SaveProximeItemsScheme(
            count=get_proxime_items_scheme.count,
            limit_accuracy=get_proxime_items_scheme.limit_accuracy,
            save=False
        )
        collection_item_scheme = TextItemScheme(
            content=collection_item.content,
            user_content_id=collection_item.user_content_id
        )
        proximity_result_scheme = await cls.find_proxime_items(
            collection_id=collection_id,
            find_proxime_items_scheme=collection_item_scheme,
            save_proxime_items_scheme=save_proxime_items_scheme,
            user=user,
            db=db
        )
        return proximity_result_scheme


collectionServ = CollectionService()
