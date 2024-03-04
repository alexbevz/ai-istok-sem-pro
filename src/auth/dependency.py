from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exception import InvalidAccessTokenException
from src.auth.model import User
from src.database import get_session_db
from src.auth.service import authServ

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: AsyncSession = Depends(get_session_db)) -> User:
    if not await authServ.is_authenticated(token):
        raise InvalidAccessTokenException()

    got_user = await authServ.get_user_by_token(token, db)
    if got_user is None:
        raise InvalidAccessTokenException()
    return got_user
