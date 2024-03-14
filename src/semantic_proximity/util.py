from typing import Union

from sentence_transformers import SentenceTransformer
from qdrant_client.local.distances import cosine_similarity, euclidean_distance, manhattan_distance

from src.semantic_proximity.config import EmbeddingConfig

embedding_config = EmbeddingConfig()

class EmbeddingUtil:

    _model = SentenceTransformer(embedding_config.get_embedding_model())

    @classmethod
    def calculate_embedding(cls, text: Union[str,list[str]]):
        return cls._model.encode(text)
    
class SimilarityUtil:

    @classmethod
    def choose_distance_metric(cls, distance_metric: str):
        if distance_metric == "cosine":
            return cosine_similarity
        elif distance_metric == "euclidean":
            return euclidean_distance
        elif distance_metric == "manhattan":
            return manhattan_distance
        return cosine_similarity

class CollectionUtil:

    @classmethod
    def convert_name_to_qdrant(cls, user_id: int, name: str):
        return f"user_{user_id}_{name}"