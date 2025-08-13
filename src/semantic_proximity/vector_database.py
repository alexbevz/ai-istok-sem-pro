from qdrant_client import QdrantClient
from src.semantic_proximity.config import QdrantConfig

class QdrantClientManager():

    def __init__(self) -> None:
        self._host: str = QdrantConfig.get_host()
        self._port: int = QdrantConfig.get_port()

    def __enter__(self) -> QdrantClient:
        # NOTE: в будущем можно переписать под AsyncQdrantClient
        self._client = QdrantClient(host=self._host,
                                    port=self._port,
                                    timeout=QdrantConfig.get_timeout())
        return self._client
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # TODO: добавить обработку исключений
        self._client.close()

