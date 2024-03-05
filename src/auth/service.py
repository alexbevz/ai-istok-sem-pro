import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import roleRep, userRep
from src.auth.scheme import ModelRoleScheme, ModelUserScheme, CreatingUserScheme, UpdatingUserScheme, TokensScheme, \
    LoginAuthScheme, RegisterAuthScheme
from src.auth.model import User, Role
from src.auth.util import BcryptUtil, JwtUtil
from src.repository import Page
from src.scheme import PageScheme
from starlette import status


class RoleService:

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list[Role]:
        got_roles = await roleRep.get_all(page=Page(), session=db)
        return got_roles

    @classmethod
    async def get_model_scheme_all(cls, db: AsyncSession) -> list[ModelRoleScheme]:
        got_roles = await cls.get_all(db)
        model_role_schemes = [ModelRoleScheme.model_validate(item, from_attributes=True) for item in got_roles]
        return model_role_schemes

    @classmethod
    async def get_all_by_id(cls, roles_id: list[int], db: AsyncSession) -> list[Role]:
        got_roles = await roleRep.get_all_by_id(models_id=roles_id, session=db)
        return got_roles


roleServ = RoleService()


class UserService:

    @classmethod
    async def create(cls, creating_user_schema: CreatingUserScheme, db: AsyncSession) -> User:
        roles = await roleServ.get_all_by_id(creating_user_schema.roles, db)
        saving_user = User(**creating_user_schema.model_dump(exclude={'roles': True}), roles=roles)
        created_user = await userRep.create(model=saving_user, session=db)
        return created_user

    @classmethod
    async def create_and_get_model_scheme(cls, creating_user_schema: CreatingUserScheme,
                                          db: AsyncSession) -> ModelUserScheme:
        created_user = await cls.create(creating_user_schema, db)
        model_user_scheme = ModelUserScheme.model_validate(created_user, from_attributes=True)
        return model_user_scheme

    @classmethod
    async def update_by_id(cls, user_id: int, update_user_schema: UpdatingUserScheme, db: AsyncSession) -> User:
        roles = await roleServ.get_all_by_id(update_user_schema.roles, db)
        updating_user = await userRep.get_by_id(model_id=user_id, session=db)
        model_data = update_user_schema.model_dump(exclude={'roles': True})
        model_data['roles'] = roles
        updating_user.update(model_data)
        updated_user = await userRep.update(model=updating_user, session=db)
        return updated_user

    @classmethod
    async def update_by_id_and_get_model_scheme(cls, user_id: int, updating_user_schema: UpdatingUserScheme,
                                                db: AsyncSession) -> ModelUserScheme:
        updated_user = await cls.update_by_id(user_id, updating_user_schema, db)
        return ModelUserScheme.model_validate(updated_user, from_attributes=True)

    @classmethod
    async def get_all(cls, page_schema: PageScheme, db: AsyncSession) -> list[User]:
        got_users = await userRep.get_all(page=Page(**page_schema.model_dump()), session=db)
        return got_users

    @classmethod
    async def get_model_scheme_all(cls, page_schema: PageScheme, db: AsyncSession) -> list[ModelUserScheme]:
        got_users = await cls.get_all(page_schema, db)
        return [ModelUserScheme.model_validate(item, from_attributes=True) for item in got_users]

    @classmethod
    async def get_by_id(cls, user_id: int, db: AsyncSession) -> User:
        got_user = await userRep.get_by_id(model_id=user_id, session=db)
        return got_user

    @classmethod
    async def get_model_scheme_by_id(cls, user_id: int, db: AsyncSession) -> ModelUserScheme:
        got_user = await cls.get_by_id(user_id, db)
        return ModelUserScheme.model_validate(got_user, from_attributes=True)

    @classmethod
    async def get_by_username(cls, username: str, db: AsyncSession) -> User:
        got_user = await userRep.get_by_unique_field(field=User.username, value=username, session=db)
        return got_user

    @classmethod
    async def delete_by_id(cls, user_id: int, db: AsyncSession) -> User:
        deleting_user = await userRep.get_by_id(model_id=user_id, session=db)
        roles = deleting_user.roles.copy()
        deleting_user.roles.clear()
        deleted_user = await userRep.delete(model=deleting_user, session=db)
        deleted_user.roles = roles
        return deleted_user

    @classmethod
    async def delete_by_id_and_get_model_scheme(cls, user_id: int, db: AsyncSession) -> ModelUserScheme:
        deleted_user = await cls.delete_by_id(user_id, db)
        return ModelUserScheme.model_validate(deleted_user, from_attributes=True, )


userServ = UserService()


class AuthService:
    # TODO and FIXME
    access_tokens = set()
    refresh_tokens = set()
    access_refresh_tokens = dict()

    @classmethod
    async def register(cls, register_auth_scheme: RegisterAuthScheme, db: AsyncSession) -> ModelUserScheme:
        encrypted_password = BcryptUtil.hash_password(register_auth_scheme.password)
        creating_user_scheme = CreatingUserScheme.model_validate({
            'username': register_auth_scheme.username,
            'password': encrypted_password,
            'email': register_auth_scheme.email,
            'roles': [2],
        })

        registered_user = await userServ.create_and_get_model_scheme(creating_user_scheme, db)
        return registered_user

    @classmethod
    async def login(cls, login_auth_scheme: LoginAuthScheme, db: AsyncSession) -> TokensScheme:
        logining_user = await userServ.get_by_username(login_auth_scheme.username, db)
        if not BcryptUtil.verify_password(login_auth_scheme.password, logining_user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect password or username')

        model_user_scheme = ModelUserScheme.model_validate(logining_user, from_attributes=True)
        payload = model_user_scheme.model_dump()
        access_token, refresh_token = JwtUtil.create_tokens(payload)
        tokens_scheme = TokensScheme(access_token=access_token, refresh_token=refresh_token)
        cls.access_tokens.add(access_token)
        cls.refresh_tokens.add(refresh_token)
        cls.access_refresh_tokens.update({access_token: refresh_token})
        return tokens_scheme

    @classmethod
    async def logout(cls, access_token: str) -> None:
        refresh_token = cls.access_refresh_tokens.get(access_token)

        if not refresh_token:
            raise HTTPException(status_code=401)

        del cls.access_refresh_tokens[access_token]
        cls.refresh_tokens.remove(refresh_token)
        cls.access_tokens.remove(access_token)

    @classmethod
    async def is_authenticated(cls, access_token: str) -> bool:
        try:
            JwtUtil.decode_token(access_token)
        except Exception as e:
            logging.error(e)
            return False
        return access_token in cls.access_tokens

    @classmethod
    async def get_user_by_token(cls, token: str, db: AsyncSession) -> User:
        if token not in cls.access_tokens:
            raise HTTPException(status_code=403, detail='Token is invalid')
        try:
            user_data = JwtUtil.decode_token(token)
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"Error: {e}")

        user_id = user_data.get('id')
        got_user = await userServ.get_by_id(user_id, db)
        return got_user
    
    @classmethod
    async def update_access_token(cls, tokens: TokensScheme) -> TokensScheme:
        if tokens.access_token not in cls.access_tokens:
            raise HTTPException(status_code=403, detail='Access token is invalid')
        if tokens.refresh_token not in cls.refresh_tokens:
            raise HTTPException(status_code=403, detail='Refresh token is invalid')
        
        cls.refresh_tokens.remove(tokens.refresh_token)
        cls.access_tokens.remove(tokens.access_token)
        del cls.access_refresh_tokens[tokens.access_token]
        try:
            user_data = JwtUtil.decode_token(tokens.refresh_token)
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"Error: {e}")
        
        access_token, refresh_token = JwtUtil.create_tokens(user_data)
        cls.access_tokens.add(access_token)
        cls.refresh_tokens.add(refresh_token)
        cls.access_refresh_tokens.update({access_token: refresh_token})
        return TokensScheme(access_token=access_token, refresh_token=refresh_token)


authServ = AuthService()
