from qdrant_client.models import Distance, VectorParams
import os

class QdrantConfig:
    _host: str = os.getenv('DB_QDRANT', 'localhost')
    _port: int = int(os.getenv('QDRANT_PORT', 6333))
    _vector_size: int = 768
    _distance_metric: Distance = Distance.COSINE
    _timeout = 32

    @classmethod
    def get_host(cls) -> str:
        return cls._host
    
    @classmethod    
    def get_port(cls) -> int:
        return cls._port
    
    @classmethod
    def get_vector_size(cls) -> int:
        return cls._vector_size
    
    @classmethod
    def get_distance_metric(cls) -> str:
        return cls._distance_metric
    
    @classmethod
    def get_vector_config(cls) -> VectorParams:
        return VectorParams(size=cls._vector_size, distance=cls._distance_metric)
    
    @classmethod
    def get_timeout(cls) -> int:
        return cls._timeout


class EmbeddingConfig:
    _embedding_model: str = os.getenv('EMBEDDING_MODEL', '/model/LaBSE') #'sentence-transformers/LaBSE'

    @classmethod
    def get_embedding_model(cls) -> str:
        return cls._embedding_model

class FileConfig:
    _max_batch_size: int = 500

    @classmethod
    def get_batch_size(cls) -> int:
        return cls._max_batch_size