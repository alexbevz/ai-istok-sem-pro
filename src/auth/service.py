import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.redis_repository import redisRep
from src.auth.repository import roleRep, userRep
from src.auth.scheme import ModelRoleScheme, ModelUserScheme, CreatingUserScheme, UpdatingUserScheme, TokensScheme, \
    LoginAuthScheme, RegisterAuthScheme
from src.auth.model import User, Role
from src.auth.util import BcryptUtil, JwtUtil
from src.repository import Page
from src.scheme import PageScheme

from src.auth.exception import (UserAlreadyExistsException,
                                UserDoesNotExistException,
                                InvalidCredentialsException,
                                InvalidTokenException)

class RoleService:

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list[Role]:
        got_roles = await roleRep.get_all(page=Page(), session=db)
        return got_roles

    @classmethod
    async def get_model_scheme_all(cls, db: AsyncSession) -> list[ModelRoleScheme]:
        got_roles = await cls.get_all(db)
        model_role_schemes = ModelRoleScheme.get_schemes_from_models(models=got_roles)
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
        schemes = ModelUserScheme.get_schemes_from_models(models=got_users)
        return schemes

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
    # TODO and FIXME: импортировать хранение токенов в redis (noSQL)

    @classmethod
    async def register(cls, register_auth_scheme: RegisterAuthScheme, db: AsyncSession) -> ModelUserScheme:
        registering_user = await userServ.get_by_username(register_auth_scheme.username, db)
        if registering_user is not None:
            raise UserAlreadyExistsException("User already exists")
        encrypted_password = BcryptUtil.hash_password(register_auth_scheme.password)
        creating_user_scheme = CreatingUserScheme.model_validate({
            'username': register_auth_scheme.username,
            'password': encrypted_password,
            'email': register_auth_scheme.email,
            'roles': [2], # роль с id 2 - user
        })

        registered_user = await userServ.create_and_get_model_scheme(creating_user_scheme, db)
        return registered_user

    @classmethod
    async def login(cls, login_auth_scheme: LoginAuthScheme, db: AsyncSession) -> TokensScheme:
        logining_user = await userServ.get_by_username(login_auth_scheme.username, db)
        if logining_user is None:
            raise UserDoesNotExistException("User does not exist")
        if not BcryptUtil.verify_password(login_auth_scheme.password, logining_user.password):
            raise InvalidCredentialsException("Incorrect password or username")
        model_user_scheme = ModelUserScheme.model_validate(logining_user, from_attributes=True)
        payload = model_user_scheme.model_dump()
        access_token, refresh_token = JwtUtil.create_tokens(payload)
        tokens_scheme = TokensScheme(access_token=access_token, refresh_token=refresh_token)
        redisRep.add_element_to_set(f"access_tokens", value=access_token)
        redisRep.add_element_to_set(f"refresh_tokens", value=refresh_token)
        redisRep.add_item_to_dict(f"access_refresh_tokens", key=access_token, value=refresh_token)
        return tokens_scheme

    @classmethod
    async def logout(cls, access_token: str) -> None:
        refresh_token = redisRep.get_value_from_dict("access_refresh_tokens", key=access_token)

        if not refresh_token:
            raise InvalidTokenException("Invalid access/refresh token pair")

        redisRep.remove_item_from_dict("access_refresh_tokens", key=access_token)
        redisRep.remove_element_from_set("access_tokens", value=access_token)
        redisRep.remove_element_from_set("refresh_tokens", value=refresh_token)

    @classmethod
    async def is_authenticated(cls, access_token: str) -> bool:
        try:
            JwtUtil.decode_token(access_token)
        except Exception as e:
            logging.error(e)
            return False
        return redisRep.get_set_element("access_tokens", access_token) is not None

    @classmethod
    async def get_user_by_token(cls, token: str, db: AsyncSession) -> User:
        if redisRep.get_set_element("access_tokens", token) is None:
            raise InvalidTokenException("Access token is invalid")
        try:
            payload = JwtUtil.decode_token(token)
        except Exception as e:
            raise InvalidTokenException(f"Error while decoding refresh token: {e}")

        user_id = payload.get('id')
        if not user_id:
            raise InvalidCredentialsException("Could not validate user id")
        got_user = await userServ.get_by_id(user_id, db)
        return got_user
    
    @classmethod
    async def update_access_token(cls, tokens: TokensScheme) -> TokensScheme:
        if redisRep.get_set_element("access_tokens", tokens.access_token) is None:
            raise InvalidTokenException("Access token is invalid")
        if redisRep.get_set_element("refresh_tokens", tokens.refresh_token) is None:
            raise InvalidTokenException("Refresh token is invalid")
        
        redisRep.remove_element_from_set("access_tokens", value=tokens.access_token)
        redisRep.remove_element_from_set("refresh_tokens", value=tokens.refresh_token)
        redisRep.remove_item_from_dict("access_refresh_tokens", key=tokens.access_token)
        try:
            user_data = JwtUtil.decode_token(tokens.refresh_token)
        except Exception as e:
            raise InvalidTokenException(f"Error while decoding refresh token: {e}")
        
        access_token, refresh_token = JwtUtil.create_tokens(user_data)
        redisRep.add_element_to_set("access_tokens", value=access_token)
        redisRep.add_element_to_set("refresh_tokens", value=refresh_token)
        redisRep.add_item_to_dict("access_refresh_tokens", key=access_token, value=refresh_token)
        return TokensScheme(access_token=access_token, refresh_token=refresh_token)


authServ = AuthService()
