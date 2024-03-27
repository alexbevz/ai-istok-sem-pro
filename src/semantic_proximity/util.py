import csv

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

class FileUtil:

    @classmethod
    def get_file_handler(cls, file_name: str):
        file_ext = file_name.split('.')[-1].lower()
        if file_ext == "csv":
            return cls._csv_reader
        else:
            return cls._default_reader
    
    @classmethod
    def _csv_reader(cls, file):
        file_content = cls._convert_bytes_to_text(file)
        reader = csv.DictReader(file_content.split('\n'),
                                fieldnames=['content', 'user_content_id'],
                                delimiter=',')
        items = [item for item in reader]
        return items

    @classmethod
    def _default_reader(cls, file):
        file_content = cls._convert_bytes_to_text(file)
        return [{"content": item,
                "user_content_id": None}
                for item in file_content.split('\n') if item.strip()]
    
    @classmethod
    def _convert_bytes_to_text(cls, file):
        return file.read().decode('utf-8')
    