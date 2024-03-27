from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.models import PointStruct
from fastapi import HTTPException
from starlette import status

from src.auth.scheme import ModelUserScheme
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
                                           ProximityRequestScheme,
                                           ProximityResponseScheme,
                                           TextProximityItemScheme,
                                           CreateDataCollectionScheme,
                                           GetDataCollectionScheme,
                                           EditDataCollectionScheme,
                                           TextItemScheme,
                                           GetAllCollectionElementsScheme,
                                           NumberOfCreatedItemsScheme)

from src.semantic_proximity.vector_repository import vectorRep
from src.semantic_proximity.config import QdrantConfig, FileConfig

embed = EmbeddingUtil.calculate_embedding

distance_metric = QdrantConfig().get_distance_metric()
distance = SimilarityUtil.choose_distance_metric(distance_metric)

qdrant_name = CollectionUtil.convert_name_to_qdrant

get_handler = FileUtil.get_file_handler

batch_size = FileConfig().get_batch_size()

class ProximityService:

    @classmethod
    async def find_proximity(cls, request: ProximityRequestScheme) -> ProximityResponseScheme:
        embedding = embed(request.content)
        compared_items = [item.content for item in request.compared_items]
        target_embeddings = embed(compared_items)
        similarities = distance(embedding, target_embeddings)
        similarity_items = [
            TextProximityItemScheme(
                content=content,
                semantic_proximity=similarity
            ) for content, similarity in zip(compared_items, similarities)
        ]
        return ProximityResponseScheme(
            content=request.content,
            compared_items_result=similarity_items
        )

proximityServ = ProximityService()

class CollectionService:

    @classmethod
    async def create_collection(cls,
                                create_collection_scheme: CreateDataCollectionScheme,
                                user: User,
                                db: AsyncSession) -> GetDataCollectionScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        qdrant_table_name = qdrant_name(user_id, create_collection_scheme.name)
        collection = await collectionRep.get_by_unique_field(field=DataCollection.qdrant_table_name,
                                                                  value=qdrant_table_name,
                                                                  session=db)
        if collection:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Collection with name {create_collection_scheme.name} already exists")
        data_collection_scheme = BaseDataCollectionScheme(
            user_id=user_id,
            name=create_collection_scheme.name,
            qdrant_table_name=qdrant_table_name)
        data_collection_model = DataCollection(**data_collection_scheme.model_dump())
        if vectorRep.create_collection(data_collection_scheme.qdrant_table_name):
        #vectorRep.create_collection(data_collection_scheme.qdrant_table_name)
            data_collection = await collectionRep.create(model=data_collection_model,
                                                          session=db)
            return GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while creating collection {create_collection_scheme.name}")


    @classmethod
    async def get_user_collections(cls,
                                   user: User,
                                   db: AsyncSession) -> list[GetDataCollectionScheme]:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collections = await collectionRep.get_all_by_field(field=DataCollection.user_id,
                                                                     value=user_id,
                                                                     session=db)
        return [GetDataCollectionScheme.model_validate(item, from_attributes=True) for item in data_collections]
    
    @classmethod
    async def get_collection_by_id(cls,
                                   collection_id: int,
                                   user: User,
                                   db: AsyncSession) -> GetDataCollectionScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                              session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        
        return GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)

    @classmethod
    async def edit_collection_by_id(cls,
                                    collection_id: int,
                                    edit_collection_scheme: EditDataCollectionScheme,
                                    user: User,
                                    db: AsyncSession) -> GetDataCollectionScheme:
        # TODO: найти реализацию переименования коллекций в qdrant
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                            session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        
        old_name = qdrant_name(user_id=user_id, name=data_collection_scheme.name)
        new_name = qdrant_name(user_id=user_id, name=edit_collection_scheme.name)
        vectorRep.create_from_collection(collection_name=new_name,
                                         base_collection=old_name)
        vectorRep.delete_collection(old_name)
        data_collection.name = edit_collection_scheme.name
        data_collection.qdrant_table_name = new_name
        data_collection = await collectionRep.update(model=data_collection, session=db)
        return GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)

    @classmethod
    async def delete_collection_by_id(cls,
                                      collection_id: int,
                                      user: User,
                                      db: AsyncSession) -> GetDataCollectionScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                              session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        vectorRep.delete_collection(data_collection.qdrant_table_name)
        data_collection = await collectionRep.delete_by_id(model_id=collection_id, session=db)
        await itemRep.delete_all_by_field(field=CollectionItem.data_collection_id,
                                          value=data_collection_scheme.id,
                                          session=db)
        return GetDataCollectionScheme.model_validate(data_collection, from_attributes=True)
    
    @classmethod
    async def add_collection_item(cls,
                                  collection_id: int,
                                  add_collection_item_scheme: TextItemScheme,
                                  user: User,
                                  db: AsyncSession) -> ModelCollectionItemScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                              session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        collection_item_scheme = BaseCollectionItemScheme(
            data_collection_id=collection_id,
            content=add_collection_item_scheme.content,
            user_content_id=add_collection_item_scheme.user_content_id
        )
        collection_item_model = CollectionItem(**collection_item_scheme.model_dump())
        collection_item = await itemRep.create(model=collection_item_model,
                                                    session=db)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item,
                                                                                from_attributes=True)
        payload = {
            "content": collection_item_scheme.content
        }
        vector = embed(add_collection_item_scheme.content)
        point = PointStruct(
            id=collection_item_scheme.id,
            payload=payload,
            vector=vector
        )
        vectorRep.add_point(collection_name=data_collection.qdrant_table_name,
                            point=point)
        return collection_item_scheme

    @classmethod
    async def add_collection_items(cls,
                                   collection_id: int,
                                   items_list: list[TextItemScheme],
                                   user: User,
                                   db: AsyncSession) -> list[ModelCollectionItemScheme]:

        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                              session=db)
        if len(items_list) > batch_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Batch is too big. Max {batch_size} items")
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                          from_attributes=True)
        if data_collection_scheme.user_id!= user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
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
        collection_items = [ModelCollectionItemScheme.model_validate(collection_item,
                                                                              from_attributes=True) for collection_item in collection_item_models]
        
        vectors = embed([item.content for item in collection_items])
        payloads = [{
            "content": item.content
        } for item in collection_items]
        points = [PointStruct(
                id=collection_item.id,
                payload=payload,
                vector=vector
            ) for collection_item, payload, vector in zip(collection_items, payloads, vectors)]
        vectorRep.add_points(collection_name=data_collection.qdrant_table_name,
                             points=points)
        return collection_items
        

    @classmethod
    async def add_collection_items_from_file(cls,
                                             collection_id: int,
                                             file,
                                             user: User,
                                             db: AsyncSession) -> NumberOfCreatedItemsScheme:
        handler = get_handler(file.filename)
        file_object = file.file
        items = handler(file_object)
        batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        response_items = []
        for batch in batches:
            item_list = [
                TextItemScheme(
                    content=item['content'],
                    user_content_id=item['user_content_id']
                ) for item in batch
            ]
            collection_items = await cls.add_collection_items(collection_id=collection_id,
                                              items_list=item_list,
                                              user=user,
                                              db=db)
            response_items.extend(collection_items)
        number_of_created_items = NumberOfCreatedItemsScheme(
            total=len(response_items)
        )
        return number_of_created_items

    @classmethod
    async def get_all_collection_items(cls,
                                       collection_id: int,
                                       offset: int,
                                       limit: int,
                                       user: User,
                                       db: AsyncSession) -> GetAllCollectionElementsScheme:

        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                            session=db) 
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        
        collection_items = await itemRep.get_all_by_field(field=CollectionItem.data_collection_id,
                                                               value=data_collection_scheme.id,
                                                               session=db)
        offset,limit = int(offset),int(limit)
        collection_items_list = [
            ModelCollectionItemScheme.model_validate(item, from_attributes=True) for item in collection_items
            ][offset:offset+limit]
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
                                  db: AsyncSession)->ModelDataCollectionScheme:
        # TODO: дописать метод позже
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                              session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        collection_item = await itemRep.get_by_id(model_id=item_id,
                                                session=db)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item,
                                                                            from_attributes=True)
        if collection_item_scheme.data_collection_id != collection_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item with id {item_id} doesn't belong to collection {collection_id}")
        return collection_item_scheme

    @classmethod
    async def get_collection_item_by_user_content_id(cls,
                                  collection_id: int,
                                  user_content_id: int,
                                  user: User,
                                  db: AsyncSession) -> ModelCollectionItemScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                              session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        collection_items = await itemRep.get_all_by_field(field=CollectionItem.user_content_id,
                                                            value=user_content_id,
                                                            session=db)
        collection_item = collection_items[0]
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item,
                                                                            from_attributes=True)
        if collection_item_scheme.data_collection_id != collection_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item with id {user_content_id} doesn't belong to collection {collection_id}")
        return collection_item_scheme

    @classmethod
    async def edit_collection_item_by_id(cls,
                                         collection_id: int,
                                         item_id: int,
                                         edit_collection_item_scheme: TextItemScheme,
                                         user: User,
                                         db: AsyncSession) -> ModelDataCollectionScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                            session=db) 
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        
        collection_item = await itemRep.get_by_id(model_id=item_id,
                                                        session=db)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        if collection_item_scheme.data_collection_id != collection_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item with id {item_id} doesn't belong to collection {collection_id}")
        collection_item.content = edit_collection_item_scheme.content
        collection_item.user_content_id = edit_collection_item_scheme.user_content_id
        collection_item = await itemRep.update(model=collection_item,
                                                    session=db)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        collection_name = data_collection_scheme.qdrant_table_name
        vector = embed(edit_collection_item_scheme.content)
        payload = {
            "content": edit_collection_item_scheme.content
        }
        point = PointStruct(
            id=collection_item_scheme.id,
            payload=payload,
            vector=vector
        )
        vectorRep.add_point(collection_name=collection_name, point=point)
        return collection_item_scheme

    @classmethod
    async def edit_collection_item_by_user_content_id(cls,
                                         collection_id: int,
                                         user_content_id: int,
                                         edit_collection_item_scheme: TextItemScheme,
                                         user: User,
                                         db: AsyncSession) -> ModelDataCollectionScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                            session=db) 
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                                    from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        
        collection_items = await itemRep.get_all_by_field(field=CollectionItem.user_content_id,
                                                         value=user_content_id,
                                                        session=db)
        collection_item = collection_items[0]
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        if collection_item_scheme.data_collection_id != collection_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item with id {user_content_id} doesn't belong to collection {collection_id}")
        collection_item.content = edit_collection_item_scheme.content
        collection_item.user_content_id = edit_collection_item_scheme.user_content_id
        collection_item = await itemRep.update(model=collection_item,
                                                    session=db)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        collection_name = data_collection_scheme.qdrant_table_name
        vector = embed(edit_collection_item_scheme.content)
        payload = {
            "content": edit_collection_item_scheme.content
        }
        point = PointStruct(
            id=collection_item_scheme.id,
            payload=payload,
            vector=vector
        )
        vectorRep.add_point(collection_name=collection_name, point=point)
        return collection_item_scheme

    @classmethod
    async def delete_collection_item(cls,
                                           collection_id: int,
                                           item_id: int,
                                           user: User,
                                           db: AsyncSession) -> ModelCollectionItemScheme:
        
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                            session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                          from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        collection_item = await itemRep.get_by_id(model_id=item_id,
                                                        session=db)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        if collection_item_scheme.data_collection_id != collection_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item with id {item_id} doesn't belong to collection {collection_id}")
        collection_item = await itemRep.delete_by_id(model_id=item_id,
                                                    session=db)
        collection_name = data_collection_scheme.qdrant_table_name
        vectorRep.delete_point_by_id(collection_name=collection_name, point_id=item_id)
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
        return collection_item_scheme

    @classmethod
    async def find_proxime_items(cls,
                                 collection_id: int,
                                 find_proxime_items_scheme: TextItemScheme,
                                 save: bool,
                                 count: int,
                                 limit_accuracy: float,
                                 user: User,
                                 db: AsyncSession)->ProximityResponseScheme:

        count, limit_accuracy = int(count), float(limit_accuracy)
        if type(save) == str:
            save = save == 'true'
        user_id = ModelUserScheme.model_validate(user, from_attributes=True).id
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                        session=db)
        if not data_collection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Collection with id {collection_id} doesn't exist")
        data_collection_scheme = ModelDataCollectionScheme.model_validate(data_collection,
                                                                          from_attributes=True)
        if data_collection_scheme.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not owner of collection {collection_id}")
        vector = embed(find_proxime_items_scheme.content)
        payload = {
            "content": find_proxime_items_scheme.content
        }
        nearest = vectorRep.find_nearest_by_vector(collection_name=data_collection_scheme.qdrant_table_name,
                                                   vector=vector)
        filtered_result = [
            TextProximityItemScheme(
                content=item.payload["content"],
                semantic_proximity=item.score
            ) for item in nearest if item.score >= limit_accuracy
        ][:count]
        if save:
            collection_item_scheme = BaseCollectionItemScheme(
                content=find_proxime_items_scheme.content,
                user_content_id=find_proxime_items_scheme.user_content_id,
                data_collection_id=collection_id,
            )
            collection_item_model = CollectionItem(**collection_item_scheme.model_dump())
            collection_item = await itemRep.create(model=collection_item_model,
                                                        session=db)
            collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)
            collection_name = data_collection_scheme.qdrant_table_name
            point = PointStruct(
                id=collection_item_scheme.id,
                payload=payload,
                vector=vector
            )
            vectorRep.add_point(collection_name=collection_name, point=point)
        
        return ProximityResponseScheme(
            content=find_proxime_items_scheme.content,
            user_content_id=find_proxime_items_scheme.user_content_id,
            compared_items_result=filtered_result
        )

    @classmethod
    async def find_proxime_items_by_id(cls,
                                       collection_id: int,
                                       item_id: int,
                                       count: int,
                                       limit_accuracy: float,
                                       user: User,
                                       db: AsyncSession)->ProximityResponseScheme:
        
        collection_item = await cls.get_collection_item_by_id(
            collection_id=collection_id,
            item_id=item_id,
            user=user,
            db=db
        )
        return await cls.find_proxime_items(
            collection_id=collection_id,
            find_proxime_items_scheme=TextItemScheme(
                content=collection_item.content,
                user_content_id=collection_item.user_content_id
            ),
            save=False,
            count=count,
            limit_accuracy=limit_accuracy,
            user=user,
            db=db
        )
    
    @classmethod
    async def find_proxime_items_by_user_content_id(cls,
                                                    collection_id: int,
                                                    user_content_id: int,
                                                    count: int,
                                                    limit_accuracy: float,
                                                    user: User,
                                                    db: AsyncSession)->ProximityResponseScheme:
        
        collection_item = await cls.get_collection_item_by_user_content_id(
            collection_id=collection_id,
            user_content_id=user_content_id,
            user=user,
            db=db
        )
        collection_item_scheme = ModelCollectionItemScheme.model_validate(collection_item, from_attributes=True)

        return await cls.find_proxime_items(
            collection_id=collection_id,
            find_proxime_items_scheme=TextItemScheme(
                content=collection_item_scheme.content,
                user_content_id=collection_item_scheme.user_content_id
            ),
            save=False,
            count=count,
            limit_accuracy=limit_accuracy,
            user=user,
            db=db
        )
        
collectionServ = CollectionService()

