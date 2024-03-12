from typing import Any, List

from qdrant_client.models import PointStruct, PointIdsList, Record

from vector_database import QdrantClientManager
from src.semantic_proximity.config import QdrantConfig

qdrant_config = QdrantConfig()


class VectorRepository:

    @classmethod
    def create_collection(cls, collection_name: str) -> str:
        with QdrantClientManager() as client:
            client.create_collection(collection_name=collection_name,
                                     vectors_config=qdrant_config.get_vector_config())
        return collection_name
    
    @classmethod
    def recreate_collection(cls, collection_name: str) -> str:
        with QdrantClientManager() as client:
            client.recreate_collection(collection_name=collection_name,
                                       vectors_config=qdrant_config.get_vector_config())
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
        with QdrantClientManager() as client:
            client.upsert(collection_name=collection_name,
                          points=[point])
    
    @classmethod
    def add_points(cls, collection_name: str, points: list[Any]):
        with QdrantClientManager() as client:
            client.upsert(collection_name=collection_name,
                          points=points)

    @classmethod
    def get_point_by_id(cls, collection_name: str, point_id: int) -> List[Record]:
        with QdrantClientManager() as client:
            return client.retrieve(collection_name=collection_name,
                                   ids=[point_id],
                                   with_payload=True,
                                   with_vectors=True)
    
    @classmethod
    def get_points_by_ids(cls, collection_name: str, point_ids: list[Any]) -> List[Record]:
        with QdrantClientManager() as client:
            return client.retrieve(collection_name=collection_name,
                                   ids=point_ids,
                                   with_payload=True,
                                   with_vectors=True)

    @classmethod
    def delete_point_by_id(cls, collection_name: str, point_id: int):
        with QdrantClientManager() as client:
            client.delete(collection_name=collection_name,
                          points_selector=PointIdsList(
                                 points=[point_id]
                                 )
                         )
    
    @classmethod
    def delete_points_by_ids(cls, collection_name: str, point_ids: list[Any]):
        with QdrantClientManager() as client:
            client.delete(collection_name=collection_name,
                          points_selector=PointIdsList(
                                 points=point_ids
                                 )
                         )

vectorRep = VectorRepository()