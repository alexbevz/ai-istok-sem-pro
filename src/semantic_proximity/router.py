from fastapi import APIRouter



class SemanticProximityRouter(APIRouter):

    def __init__(self):
        super().__init__(prefix='/sps', tags=['Семантическая близость'])
    



sps_router = SemanticProximityRouter()

