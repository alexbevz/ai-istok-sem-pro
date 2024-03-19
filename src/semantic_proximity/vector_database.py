from qdrant_client import QdrantClient
from src.semantic_proximity.config import QdrantConfig

qdrant_config = QdrantConfig()

class QdrantClientManager():

    def __init__(self) -> None:
        self._host: str = qdrant_config.get_host()
        self._port: int = qdrant_config.get_port()

    def __enter__(self) -> QdrantClient:
        # NOTE: в будущем можно переписать под AsyncQdrantClient
        self._client = QdrantClient(host=self._host,
                                    port=self._port)
        return self._client
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # TODO: добавить обработку исключений
        self._client.close()

