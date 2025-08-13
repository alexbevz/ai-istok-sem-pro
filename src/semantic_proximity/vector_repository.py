from typing import Any, List

from qdrant_client.models import PointStruct, PointIdsList, Record, InitFrom

from src.semantic_proximity.vector_database import QdrantClientManager
from src.semantic_proximity.config import QdrantConfig
from src.semantic_proximity.exception import QdrantCollectionException

class VectorRepository:

    @classmethod
    def create_collection(cls, collection_name: str) -> str:
        with QdrantClientManager() as client:
            vector_config = QdrantConfig.get_vector_config()
            success = client.create_collection(collection_name=collection_name,
                                     vectors_config=vector_config)
            if not success:
                raise QdrantCollectionException(f"Could not create collection {collection_name}")
            return collection_name
    
    @classmethod
    def recreate_collection(cls, collection_name: str) -> str:
        with QdrantClientManager() as client:
            vector_congif = QdrantConfig.get_vector_config()
            client.recreate_collection(collection_name=collection_name,
                                       vectors_config=vector_congif)
        return collection_name
    
    @classmethod
    def create_from_collection(cls, collection_name: str, base_collection: str) -> str:
        with QdrantClientManager() as client:
            init_collection = InitFrom(collection=base_collection)
            vector_config = QdrantConfig.get_vector_config()
            client.create_collection(collection_name=collection_name,
                                     vectors_config=vector_config,
                                     init_from=init_collection)
        return collection_name

    @classmethod
    def delete_collection(cls, collection_name: str) -> str:
        with QdrantClientManager() as client:
            client.delete_collection(collection_name=collection_name)
        return collection_name
    
    @classmethod
    def get_collection_len(cls, collection_name: str) -> int:
        with QdrantClientManager() as client:
            return client.count(collection_name=collection_name).count

    @classmethod
    def add_point(cls, collection_name: str, point: PointStruct):
        cls.add_points(collection_name, [point])
    
    @classmethod
    def add_points(cls, collection_name: str, points: list[Any]):
        with QdrantClientManager() as client:
            client.upsert(collection_name=collection_name,
                          points=points)

    @classmethod
    def get_point_by_id(cls, collection_name: str, point_id: int) -> List[Record]:
        return cls.get_points_by_ids(collection_name, [point_id])
    
    @classmethod
    def get_points_by_ids(cls, collection_name: str, point_ids: list[Any]) -> List[Record]:
        with QdrantClientManager() as client:
            return client.retrieve(collection_name=collection_name,
                                   ids=point_ids,
                                   with_payload=True,
                                   with_vectors=True)

    @classmethod
    def delete_point_by_id(cls, collection_name: str, point_id: int):
        cls.delete_points_by_ids(collection_name, [point_id])
    
    @classmethod
    def delete_points_by_ids(cls, collection_name: str, point_ids: list[Any]):
        with QdrantClientManager() as client:
            points = PointIdsList(points=point_ids)
            client.delete(collection_name=collection_name,
                          points_selector=points
                         )
    
    @classmethod
    def find_nearest_by_vector(cls, collection_name: str, vector, limit: int):
        with QdrantClientManager() as client:
            return client.search(collection_name=collection_name,
                               query_vector=vector,
                               limit=limit,
                               with_payload=True,
                               with_vectors=True)

vectorRep = VectorRepository()