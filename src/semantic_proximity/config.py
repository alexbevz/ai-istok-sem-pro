from qdrant_client.models import Distance, VectorParams
from os import getenv
class QdrantConfig:
    _host: str = getenv('DB_QDRANT', 'localhost')
    _port: int = 6333
    _vector_size: int = 768
    _distance_metric: Distance = Distance.COSINE

    def get_host(self) -> str:
        return self._host
    
    def get_port(self) -> int:
        return self._port

    def get_vector_size(self) -> int:
        return self._vector_size
    
    def get_distance_metric(self) -> str:
        return self._distance_metric
    
    def get_vector_config(self) -> VectorParams:
        return VectorParams(size=self._vector_size, distance=self._distance_metric)


class EmbeddingConfig:
    _embedding_model: str = '/model/LaBSE'#'sentence-transformers/LaBSE'

    def get_embedding_model(self) -> str:
        return self._embedding_model

