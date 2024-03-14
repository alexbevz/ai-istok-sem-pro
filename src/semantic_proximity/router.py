from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session_db

from src.auth.dependency import get_current_user
from src.auth.model import User

from src.semantic_proximity.service import proximityServ, collectionServ
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
                                           TextItemScheme)


class SemanticProximityRouter(APIRouter):

    def __init__(self):
        super().__init__(prefix='/sps', tags=['Семантическая близость'])
        self.add_api_route(endpoint=self.find_proximity, path="/find", methods=['GET'])

        self.add_api_route(endpoint=self.create_collection, path="/collections", methods=['POST'])
        self.add_api_route(endpoint=self.get_all_collections, path="/collections", methods=['GET'])
        self.add_api_route(endpoint=self.get_collection, path="/collections/{collection_id}", methods=['GET'])
        self.add_api_route(endpoint=self.delete_collection, path="/collections/{collection_id}", methods=['DELETE'])

        self.add_api_route(endpoint=self.add_collection_item, path="/collections/{collection_id}/items", methods=['POST'])


    @classmethod
    async def find_proximity(cls, proximity_request_scheme: ProximityRequestScheme):
        proximity_response = await proximityServ.find_proximity(proximity_request_scheme)
        return proximity_response

    @classmethod
    async def create_collection(cls,
                                create_collection_scheme: CreateDataCollectionScheme,
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_session_db)):
        
        collection = await collectionServ.create_collection(create_collection_scheme, user, db)
        return collection
    
    @classmethod
    async def get_all_collections(cls,
                                  user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_session_db)):
        
        collections = await collectionServ.get_user_collections(user, db)
        return collections

    @classmethod
    async def get_collection(cls,
                             collection_id: int,
                             user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_session_db)):
        
        collection = await collectionServ.get_collection_by_id(collection_id, user, db)
        return collection

    @classmethod
    async def delete_collection(cls,
                                collection_id: int,
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_session_db)):
        
        collection = await collectionServ.delete_collection_by_id(collection_id, user, db)
        return collection


    @classmethod
    async def add_collection_item(cls,
                                  collection_id: int,
                                  add_collection_item_scheme: TextItemScheme,
                                  user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_session_db)):
        
        collection_item = await collectionServ.add_collection_item(collection_id, add_collection_item_scheme, user, db)
        return collection_item
    
    

spsRouter = SemanticProximityRouter()

