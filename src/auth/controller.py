from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.scheme import CreatingRoleScheme, UpdatingRoleScheme, CreatingUserScheme, UpdatingUserScheme, PageScheme, \
    ModelRoleScheme
from src.auth.dependency import get_current_user, RoleChecker
from src.auth.model import User
from src.auth.service import RoleService as roleServ, UserService as userServ
from src.database import get_session_db


class RoleRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix='/roles', tags=['Роли'], dependencies=[Depends(RoleChecker({'admin'}))])
        self.add_api_route(endpoint=self.save, path='/', methods=['POST'])
        self.add_api_route(endpoint=self.save_all, path='/all', methods=['POST'])
        self.add_api_route(endpoint=self.update_by_id, path='/{role_id}', methods=['PATCH'])
        self.add_api_route(endpoint=self.get_all, path='/all', methods=['GET'], dependencies=[Depends(PageScheme)])
        self.add_api_route(endpoint=self.get_by_id, path='/{role_id}', methods=['GET'],
                           dependencies=[Depends(RoleChecker({'user'}))])
        self.add_api_route(endpoint=self.delete_all_by_id, path='/all', methods=['DELETE'])
        self.add_api_route(endpoint=self.delete_by_id, path='/{role_id}', methods=['DELETE'])

    @classmethod
    async def save(cls, creating_role_schema: CreatingRoleScheme, auth_user: Annotated[User, Depends(get_current_user)],
                   db: AsyncSession = Depends(get_session_db)) -> ModelRoleScheme:
        role_schema = await roleServ.save(creating_role_schema, db)
        print(auth_user)
        return role_schema

    @classmethod
    async def save_all(cls, all_save_role_schema: list[CreatingRoleScheme], db: AsyncSession = Depends(get_session_db)):
        roles_schema = await roleServ.save_all(all_save_role_schema, db)
        return roles_schema

    @classmethod
    async def update_by_id(cls, role_id: int, role_update: UpdatingRoleScheme,
                           db: AsyncSession = Depends(get_session_db)):
        role_schema = await roleServ.update_by_id(role_id, role_update, db)
        return role_schema

    @classmethod
    async def get_by_id(cls, role_id: int, db: AsyncSession = Depends(get_session_db)):
        role_schema = await roleServ.get_by_id(role_id, db)
        return role_schema

    @classmethod
    async def get_all(cls, page_schema: PageScheme = Depends(), db: AsyncSession = Depends(get_session_db)):
        roles_schema = await roleServ.get_all(page_schema, db)
        return roles_schema

    @classmethod
    async def delete_by_id(cls, role_id: int, db: AsyncSession = Depends(get_session_db)):
        role_schema = await roleServ.delete_by_id(role_id, db)
        return role_schema

    @classmethod
    async def delete_all_by_id(cls, models_id: list[int], db: AsyncSession = Depends(get_session_db)):
        roles_schema = await roleServ.delete_all_by_id(models_id, db)
        return roles_schema


class UserRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix='/users', tags=['Пользователи'])
        self.add_api_route(endpoint=self.save, path='/', methods=['POST'])
        self.add_api_route(endpoint=self.update_by_id, path='/{user_id}', methods=['PATCH'])
        self.add_api_route(endpoint=self.get_all, path='/all', methods=['GET'])
        self.add_api_route(endpoint=self.get_by_id, path='/{user_id}', methods=['GET'])
        self.add_api_route(endpoint=self.delete_by_id, path='/{user_id}', methods=['DELETE'])

    @classmethod
    async def save(cls, save_user_schema: CreatingUserScheme, db: AsyncSession = Depends(get_session_db)):
        saved_user = await userServ.save(save_user_schema, db)
        return saved_user

    @classmethod
    async def update_by_id(cls, user_id: int, updated_user_schema: UpdatingUserScheme,
                           db: AsyncSession = Depends(get_session_db)):
        updated_user = await userServ.update_by_id(user_id, updated_user_schema, db)
        return updated_user

    @classmethod
    async def get_all(cls, page_scheme: PageScheme = Depends(), db: AsyncSession = Depends(get_session_db)):
        got_users = await userServ.get_all(page_scheme, db)
        return got_users

    @classmethod
    async def get_by_id(cls, user_id: int, db: AsyncSession = Depends(get_session_db)):
        got_user = await userServ.get_model_scheme_by_id(user_id, db)
        return got_user

    @classmethod
    async def delete_by_id(cls, user_id: int, db: AsyncSession = Depends(get_session_db)):
        deleted_user = await userServ.delete_by_id(user_id, db)
        return deleted_user


class AuthRouter(APIRouter):

    def __init__(self):
        super().__init__(prefix='/auth', tags=['Авторизация'])
        self.add_api_route(endpoint=self.login, path='/login', methods=['POST'], )
        self.add_api_route(endpoint=self.check, path='/check', methods=['POST'], )
        self.add_api_route(endpoint=self.update_access_token, path='/tokens/access', methods=['POST'], )
        self.add_api_route(endpoint=self.update_refresh_token, path='/tokens/refresh', methods=['POST'], )
        self.add_api_route(endpoint=self.logout, path='/logout', methods=['POST'], )

    @classmethod
    async def login(cls):
        pass

    @classmethod
    async def check(cls):
        pass

    @classmethod
    async def update_access_token(cls):
        pass

    @classmethod
    async def update_refresh_token(cls):
        pass

    @classmethod
    async def logout(cls):
        pass


roleRouter = RoleRouter()
userRouter = UserRouter()
authRouter = AuthRouter()
