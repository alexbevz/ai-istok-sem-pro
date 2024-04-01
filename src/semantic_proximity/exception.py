class CollectionNotExistsException(Exception):
    pass

class InsuffucientAccessRightsException(Exception):
    pass

class BatchSizeException(Exception):
    pass

class CollectionAlreadyExistsException(Exception):
    pass

class WrongCollectionException(Exception):
    pass

class QdrantCollectionException(Exception):
    pass