from src.repository import CrudRepository
from src.semantic_proximity.model import DataCollection, CollectionItem

class DataCollectionRepository(CrudRepository, cls_model=DataCollection):
    pass

collectionRep = DataCollectionRepository()

class CollectionItemRepository(CrudRepository, cls_model=CollectionItem):
    pass

itemRep = CollectionItemRepository()