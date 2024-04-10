from fastapi.responses import JSONResponse
from starlette import status

from src.exception import CrudException, TeapotException
from src.auth.exception import UserNotAuthorizedException, InvalidAccessTokenException, HttpForbiddenException

from src.auth.exception import (UserAlreadyExistsException,
                                UserDoesNotExistException,
                                InvalidCredentialsException,
                                InvalidTokenException)

from src.semantic_proximity.exception import (CollectionAlreadyExistsException,
                                              CollectionDoesNotExistException,
                                              CollectionItemDoesNotExistException,
                                              WrongCollectionException,
                                              BatchSizeException,
                                              InsuffucientAccessRightsException,
                                              QdrantCollectionException,
                                              MissingFileColumnsException)

from pydantic import ValidationError

def get_400_bad_request_response(exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"{exc}"}
    )

def get_401_unauthorized_response(exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": f"{exc}"}
    )

def get_403_forbidden_response(exc):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": f"{exc}"}
    )

def get_404_not_found_response(exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"{exc}"}
    )

def get_409_conflict_response(exc):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": f"{exc}"}
    )

def get_500_internal_server_error_response(exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"{exc}"}
    )

def get_418_teapot_response(exc):
    """Joke response"""
    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={"detail": f"{exc}"}
    )

async def crud_exception_handler(request, exc: CrudException):
    return get_400_bad_request_response(exc)

async def wrong_collection_exception_handler(request, exc: WrongCollectionException):
    return get_400_bad_request_response(exc)

async def batch_size_exception_handler(request, exc: BatchSizeException):
    return get_400_bad_request_response(exc)

async def missing_file_columns_exception_handler(request, exc: MissingFileColumnsException):
    return get_400_bad_request_response(exc)

async def validation_error_handler(request, exc: ValidationError):
    return get_400_bad_request_response(exc)

async def user_not_authorized_exception_handler(request, exc: UserNotAuthorizedException):
    return get_401_unauthorized_response(exc)

async def invalid_access_token_exception_handler(request, exc: InvalidAccessTokenException):
    return get_401_unauthorized_response(exc)

async def invalide_credentials_exception_handler(request, exc: InvalidCredentialsException):
    return get_401_unauthorized_response(exc)

async def http_forbidden_exception_handler(request, exc: HttpForbiddenException):
    return get_403_forbidden_response(exc)

async def insuffucient_access_rights_exception_handler(request, exc: InsuffucientAccessRightsException):
    return get_403_forbidden_response(exc)

async def invalid_token_exception_handler(request, exc: InvalidTokenException):
    return get_403_forbidden_response(exc)

async def collection_not_exists_exception_handler(request, exc: CollectionDoesNotExistException):
    return get_404_not_found_response(exc)

async def user_does_not_exist_exception_handler(request, exc: UserDoesNotExistException):
    return get_404_not_found_response(exc)

async def collection_item_does_not_exits_exception_handler(request, exc: CollectionItemDoesNotExistException):
    return get_404_not_found_response(exc)

async def collection_already_exists_exception_handler(request, exc: CollectionAlreadyExistsException):
    return get_409_conflict_response(exc)

async def user_already_exists_exception_handler(request, exc: UserAlreadyExistsException):
    return get_409_conflict_response(exc)

async def qdrant_collection_exception_handler(request, exc: QdrantCollectionException):
    return get_500_internal_server_error_response(exc)

async def teapot_exception_handler(request, exc: TeapotException):
    """Joke handler for teapot exception"""
    return get_418_teapot_response

exception_handlers = {
    TeapotException:                    teapot_exception_handler,
    CrudException:                      crud_exception_handler,
    UserNotAuthorizedException:         user_not_authorized_exception_handler,
    InvalidAccessTokenException:        invalid_access_token_exception_handler,
    InvalidCredentialsException:        invalide_credentials_exception_handler,
    HttpForbiddenException:             http_forbidden_exception_handler,
    CollectionDoesNotExistException:    collection_not_exists_exception_handler,
    InsuffucientAccessRightsException:  insuffucient_access_rights_exception_handler,
    BatchSizeException:                 batch_size_exception_handler,
    CollectionAlreadyExistsException:   collection_already_exists_exception_handler,
    UserAlreadyExistsException:         user_already_exists_exception_handler,
    WrongCollectionException:           wrong_collection_exception_handler,
    QdrantCollectionException:          qdrant_collection_exception_handler,
    MissingFileColumnsException:        missing_file_columns_exception_handler,
    ValidationError:                    validation_error_handler
}
