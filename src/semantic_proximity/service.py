from sqlalchemy.ext.asyncio import AsyncSession

from src.semantic_proximity.util import (EmbeddingUtil,
                                         SimilarityUtil)

from src.semantic_proximity.repository import (collectionRep,
                                               itemRep)

from src.semantic_proximity.scheme import (DataCollectionScheme,
                                           CollectionItemScheme,
                                           FindProximityRequest,
                                           FindProximityResponse,
                                           TextProximityItemScheme)

from src.semantic_proximity.vector_repository import vectorRep
from src.semantic_proximity.config import QdrantConfig

embed = EmbeddingUtil.calculate_embedding

distance_metric = QdrantConfig().get_distance_metric()
distance = SimilarityUtil.choose_distance_metric(distance_metric)

class ProximityService:

    @classmethod
    def find_proximity(cls, request: FindProximityRequest) -> FindProximityResponse:
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
        return FindProximityResponse(
            content=request.content,
            compared_items_result=similarity_items
        )


class CollectionService:

    @classmethod
    async def create_collection(cls, data_collection_scheme: DataCollectionScheme,
                          db: AsyncSession) -> DataCollectionScheme:
        
        data_collection = await collectionRep.create(model=data_collection_scheme,
                                                          session=db)
        return data_collection

