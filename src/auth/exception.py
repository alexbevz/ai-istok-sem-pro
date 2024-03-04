from fastapi import HTTPException
from starlette import status


class UserNotAuthorizedException(Exception):
    pass


class InvalidAccessTokenException(HTTPException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


class HttpForbiddenException(HTTPException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Insufficient access rights',
        )
