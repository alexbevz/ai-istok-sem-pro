from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exception import InvalidAccessTokenException, HttpForbiddenException
from src.auth.model import User
from src.database import get_session_db
from src.auth.service import authServ

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: AsyncSession = Depends(get_session_db)) -> User:
    if not await authServ.is_authenticated(token):
        raise InvalidAccessTokenException()

    got_user = await authServ.get_user_by_token(token, db)
    if got_user is None:
        raise InvalidAccessTokenException()
    return got_user


class RoleChecker:

    def __init__(self, required_roles: set[str], ):
        self.required_roles = required_roles

    def __call__(self, user: Annotated[User, get_current_user]) -> None:
        user_roles = set()

        for role in user.roles:
            user_roles.add(role.name)

        is_check = self.required_roles.issubset(user_roles)

        if not is_check:
            raise HttpForbiddenException()
