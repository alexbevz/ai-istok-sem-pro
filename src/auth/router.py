from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependency import get_current_user, RoleChecker, oauth2_scheme
from src.auth.model import User
from src.auth.scheme import UpdatingUserScheme, LoginAuthScheme, RegisterAuthScheme
from src.auth.service import roleServ, userServ, authServ
from src.database import get_session_db
from src.scheme import PageScheme


class RoleRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix='/roles', tags=['Роли'], dependencies=[Depends(RoleChecker({'admin'}))])
        self.add_api_route(endpoint=self.get_all, path='/all', methods=['GET'])

    @classmethod
    async def get_all(cls, db: AsyncSession = Depends(get_session_db)):
        roles_schema = await roleServ.get_model_scheme_all(db)
        return roles_schema


class UserRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix='/users', tags=['Пользователи'], dependencies=[Depends(RoleChecker({'admin'}))])
        self.add_api_route(endpoint=self.get_me, path='/me}', methods=['GET'],
                           dependencies=[Depends(RoleChecker({'user'}))])
        self.add_api_route(endpoint=self.get_all, path='/all', methods=['GET'])
        self.add_api_route(endpoint=self.get_by_id, path='/{user_id}', methods=['GET'])
        self.add_api_route(endpoint=self.update_by_id, path='/{user_id}', methods=['PATCH'],
                           dependencies=[Depends(RoleChecker({'user'}))])
        self.add_api_route(endpoint=self.delete_by_id, path='/{user_id}', methods=['DELETE'])


    @classmethod
    async def get_me(cls, user: Annotated[User, Depends(get_current_user)], db: AsyncSession = Depends(get_session_db)):
        got_user = await userServ.get_model_scheme_by_id(user.id, db)
        return got_user

    @classmethod
    async def get_all(cls, page_scheme: PageScheme = Depends(), db: AsyncSession = Depends(get_session_db)):
        got_users = await userServ.get_model_scheme_all(page_scheme, db)
        return got_users

    @classmethod
    async def get_by_id(cls, user_id: int, db: AsyncSession = Depends(get_session_db)):
        got_user = await userServ.get_model_scheme_by_id(user_id, db)
        return got_user

    @classmethod
    async def update_by_id(cls, user_id: int, updated_user_schema: UpdatingUserScheme,
                           db: AsyncSession = Depends(get_session_db)):
        updated_user = await userServ.update_by_id_and_get_model_scheme(user_id, updated_user_schema, db)
        return updated_user

    @classmethod
    async def delete_by_id(cls, user_id: int, db: AsyncSession = Depends(get_session_db)):
        deleted_user = await userServ.delete_by_id_and_get_model_scheme(user_id, db)
        return deleted_user


class AuthRouter(APIRouter):

    def __init__(self):
        super().__init__(prefix='/auth', tags=['Авторизация'])
        self.add_api_route(endpoint=self.register, path='/register', methods=['POST'], )
        self.add_api_route(endpoint=self.login, path='/login', methods=['POST'], )
        self.add_api_route(endpoint=self.check, path='/check', methods=['POST'], )
        # self.add_api_route(endpoint=self.update_access_token, path='/tokens/access', methods=['POST'], )
        # self.add_api_route(endpoint=self.update_refresh_token, path='/tokens/refresh', methods=['POST'], )
        self.add_api_route(endpoint=self.logout, path='/logout', methods=['POST'], )

    @classmethod
    async def register(cls, register_auth_scheme: RegisterAuthScheme, db: AsyncSession = Depends(get_session_db)):
        model_user_scheme = await authServ.register(register_auth_scheme, db)
        return model_user_scheme

    @classmethod
    async def login(cls, login_auth_scheme: LoginAuthScheme, db: AsyncSession = Depends(get_session_db)):
        tokens_scheme = await authServ.login(login_auth_scheme, db)
        return tokens_scheme

    @classmethod
    async def check(cls, token: Annotated[str, Depends(oauth2_scheme)]):
        await authServ.is_authenticated(token)

    @classmethod
    async def update_access_token(cls):
        pass

    @classmethod
    async def update_refresh_token(cls):
        pass

    @classmethod
    async def logout(cls, token: Annotated[str, Depends(oauth2_scheme)]):
        await authServ.logout(token)


roleRouter = RoleRouter()
userRouter = UserRouter()
authRouter = AuthRouter()
