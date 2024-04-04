from fastapi.responses import JSONResponse
from starlette import status

from src.exception import CrudException, TeapotException
from src.auth.exception import UserNotAuthorizedException, InvalidAccessTokenException, HttpForbiddenException

from src.semantic_proximity.exception import (CollectionAlreadyExistsException,
                                              CollectionNotExistsException,
                                              WrongCollectionException,
                                              BatchSizeException,
                                              InsuffucientAccessRightsException,
                                              QdrantCollectionException,
                                              MissingFileColumnsException)

from pydantic import ValidationError

async def teapot_exception_handler(request, exc: TeapotException):
    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={"detail": f"{exc}"}
    )

async def crud_exception_handler(request, exc: CrudException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"{exc}"}
    )

async def user_not_authorized_exception_handler(request, exc: UserNotAuthorizedException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": f"{exc}"}
    )

async def invalid_access_token_exception_handler(request, exc: InvalidAccessTokenException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": f"{exc}"}
    )

async def http_forbidden_exception_handler(request, exc: HttpForbiddenException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": f"{exc}"}
    )

async def collection_not_exists_exception_handler(request, exc: CollectionNotExistsException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"{exc}"}
    )

async def insuffucient_access_rights_exception_handler(request, exc: InsuffucientAccessRightsException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": f"{exc}"}
    )

async def batch_size_exception_handler(request, exc: BatchSizeException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"{exc}"}
    )

async def collection_already_exists_exception_handler(request, exc: CollectionAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": f"{exc}"}
    )

async def wrong_collection_exception_handler(request, exc: WrongCollectionException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"{exc}"}
    )

async def qdrant_collection_exception_handler(request, exc: QdrantCollectionException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"{exc}"}
    )

async def missing_file_columns_exception_handler(request, exc: MissingFileColumnsException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"{exc}"}
    )

async def validation_error_handler(request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"{exc}"}
    )

exception_handlers = {
    TeapotException: teapot_exception_handler,
    CrudException: crud_exception_handler,
    UserNotAuthorizedException: user_not_authorized_exception_handler,
    InvalidAccessTokenException: invalid_access_token_exception_handler,
    HttpForbiddenException: http_forbidden_exception_handler,
    CollectionNotExistsException: collection_not_exists_exception_handler,
    InsuffucientAccessRightsException: insuffucient_access_rights_exception_handler,
    BatchSizeException: batch_size_exception_handler,
    CollectionAlreadyExistsException: collection_already_exists_exception_handler,
    WrongCollectionException: wrong_collection_exception_handler,
    QdrantCollectionException: qdrant_collection_exception_handler,
    MissingFileColumnsException: missing_file_columns_exception_handler,
    ValidationError: validation_error_handler
}
