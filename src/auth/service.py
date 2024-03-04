from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import RoleRepository, UserRepository
from src.auth.scheme import ModelRoleScheme, CreatingRoleScheme, UpdatingRoleScheme, ModelUserScheme, \
    CreatingUserScheme, \
    UpdatingUserScheme, PageScheme
from src.auth.model import User, Role
from src.repository import Page


class RoleService:
    role_rep: RoleRepository = RoleRepository()

    @classmethod
    async def save(cls, save_role_schema: CreatingRoleScheme, db: AsyncSession) -> ModelRoleScheme:
        saving_model = Role(**save_role_schema.model_dump())
        saved_role = await cls.role_rep.create(model=saving_model, session=db)
        return ModelRoleScheme.model_validate(saved_role, from_attributes=True)

    @classmethod
    async def save_all(cls, all_save_role_schema: list[CreatingRoleScheme], db: AsyncSession) -> list[ModelRoleScheme]:
        roles = [Role(**item.model_dump()) for item in all_save_role_schema]
        saved_role_all = await cls.role_rep.create_all(models=roles, session=db)
        return [ModelRoleScheme.model_validate(item, from_attributes=True) for item in saved_role_all]

    @classmethod
    async def get_all(cls, page_schema: PageScheme, db: AsyncSession) -> list[ModelRoleScheme]:
        got_roles = await cls.role_rep.get_all(page=Page(**page_schema.model_dump()), session=db)
        return [ModelRoleScheme.model_validate(item, from_attributes=True) for item in got_roles]

    @classmethod
    async def get_by_id(cls, role_id: int, db: AsyncSession) -> ModelRoleScheme:
        got_role = await cls.role_rep.get_by_id(model_id=role_id, session=db)
        return ModelRoleScheme.model_validate(got_role, from_attributes=True)

    @classmethod
    async def update_by_id(cls, role_id: int, update_role_schema: UpdatingRoleScheme, db: AsyncSession) -> ModelRoleScheme:
        updating_role = await cls.role_rep.get_by_id(model_id=role_id, session=db)
        updating_role.update(update_role_schema.model_dump())
        updated_role = await cls.role_rep.update(model=updating_role, session=db)
        return ModelRoleScheme.model_validate(updated_role, from_attributes=True)

    @classmethod
    async def delete_by_id(cls, role_id: int, db: AsyncSession) -> ModelRoleScheme:
        deleted_role = await cls.role_rep.delete_by_id(model_id=role_id, session=db)
        return ModelRoleScheme.model_validate(deleted_role, from_attributes=True)

    @classmethod
    async def delete_all_by_id(cls, models_id: list[int], db: AsyncSession) -> list[ModelRoleScheme]:
        deleted_roles = await cls.role_rep.delete_all_by_id(models_id=models_id, session=db)
        return [ModelRoleScheme.model_validate(item, from_attributes=True) for item in deleted_roles]


class UserService:
    user_rep: UserRepository = UserRepository()
    role_rep: RoleRepository = RoleRepository()

    @classmethod
    async def _create_user(cls, save_user_schema: CreatingUserScheme, db: AsyncSession) -> User:
        roles = await cls.role_rep.get_all_by_id(models_id=save_user_schema.roles, session=db)
        saving_user = User(**save_user_schema.model_dump(exclude={'roles': True}), roles=roles)
        saved_user = await cls.user_rep.create(model=saving_user, session=db)
        return saved_user

    @classmethod
    async def _update_user_by_id(cls, user_id: int, update_user_schema: UpdatingUserScheme, db: AsyncSession) -> User:
        roles = await cls.role_rep.get_all_by_id(models_id=update_user_schema.roles, session=db)
        updating_user = await cls.user_rep.get_by_id(model_id=user_id, session=db)
        model_data = update_user_schema.model_dump(exclude={'roles': True})
        model_data['roles'] = roles
        updating_user.update(model_data)
        updated_user = await cls.user_rep.update(model=updating_user, session=db)
        return updated_user

    @classmethod
    async def save(cls, save_user_schema: CreatingUserScheme, db: AsyncSession) -> ModelUserScheme:
        saved_user = await cls._create_user(save_user_schema, db)
        return ModelUserScheme.model_validate(saved_user, from_attributes=True)

    @classmethod
    async def update_by_id(cls, user_id: int, update_user_schema: UpdatingUserScheme, db: AsyncSession):
        updated_user = await cls._update_user_by_id(user_id, update_user_schema, db)
        return ModelUserScheme.model_validate(updated_user, from_attributes=True)

    @classmethod
    async def get_all(cls, page_schema: PageScheme, db: AsyncSession) -> list[ModelUserScheme]:
        got_users = await cls.user_rep.get_all(page=Page(**page_schema.model_dump()), session=db)
        return [ModelUserScheme.model_validate(item, from_attributes=True) for item in got_users]

    @classmethod
    async def get_by_id(cls, user_id: int, db: AsyncSession) -> User:
        got_user = await cls.user_rep.get_by_id(model_id=user_id, session=db)
        return got_user

    @classmethod
    async def get_model_scheme_by_id(cls, user_id: int, db: AsyncSession) -> ModelUserScheme:
        got_user = await cls.get_by_id(user_id, db)
        return ModelUserScheme.model_validate(got_user, from_attributes=True)

    @classmethod
    async def delete_by_id(cls, user_id: int, db: AsyncSession) -> ModelUserScheme:
        deleting_user = await cls.user_rep.get_by_id(model_id=user_id, session=db)
        roles = deleting_user.roles.copy()
        deleting_user.roles.clear()
        deleted_user = await cls.user_rep.delete(model=deleting_user, session=db)
        deleted_user.roles = roles
        return ModelUserScheme.model_validate(deleted_user, from_attributes=True, )


userServ = UserService()


class AuthService:

    @classmethod
    async def authenticate(cls):
        pass

    @classmethod
    async def is_authenticated(cls):
        pass

    @classmethod
    async def get_user_by_token(cls, db: AsyncSession) -> User:
        return await userServ.get_by_id(1, db)


authServ = AuthService()
