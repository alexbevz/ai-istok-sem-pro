import asyncio
from typing import Type, Any, Sequence

from src.repository import CrudRepository
from src.auth.model import Role, User, UserRole
from src.auth.scheme import PageSchema
from src.database import get_session_db
from sqlalchemy import select, Row, delete
from sqlalchemy.ext.asyncio import AsyncSession


class RoleRepository(CrudRepository, cls_model=Role):
    pass


class UserRoleRepository(CrudRepository, cls_model=UserRole):
    pass


class UserRepository(CrudRepository, cls_model=User):
    pass

# class RoleRepository:
#
#     @staticmethod
#     async def save(role: Role) -> Role:
#         async with await get_session_db() as session:
#             session.add(role)
#             await session.commit()
#         return role
#
#     @staticmethod
#     async def get_by_id(role_id: int) -> Type[Role]:
#         async with await get_session_db() as session:
#             role = await session.get(Role, role_id)
#         return role
#
#     @staticmethod
#     async def get_all(page: PageSchema) -> Sequence[Row[tuple[Any, ...] | Any]]:
#         async with await get_session_db() as session:
#             rows = await session.execute(
#                 select(Role)
#                 .offset(page.offset)
#                 .limit(page.limit)
#             )
#             roles = rows.all()
#         return roles
#
#     @staticmethod
#     async def update(role_id: int, changes: dict) -> Role:
#         async with await get_session_db() as session:
#             updated_role = await session.get(Role, role_id)
#             updated_role.update(changes)
#             await session.commit()
#         return updated_role
#
#     @staticmethod
#     async def delete_by_id(role_id: int) -> None:
#         async with await get_session_db() as session:
#             await session.execute(delete(Role).where(Role.id == role_id))
#             await session.commit()


# class UserRepository(CrudRepository, cls_model=User):
#     pass
# _session: AsyncSession
# async def start_new_session(self):
#     self._session = await

# def __init__(self):
#     self.start_new_session()
#     super().__init__(session=self._session)

# @staticmethod
# async def save(user: User) -> User:
#     async with await get_session_db() as session:
#         session.add(user)
#         await session.commit()
#     return user
#
# @staticmethod
# async def get_by_id(role_id: int) -> Type[Role]:
#     async with await get_session_db() as session:
#         role = await session.get(Role, role_id)
#     return role
#
# @staticmethod
# async def get_all(page: PageSchema) -> Sequence[Row[tuple[Any, ...] | Any]]:
#     async with await get_session_db() as session:
#         rows = await session.execute(
#             select(Role)
#             .offset(page.offset)
#             .limit(page.limit)
#         )
#         roles = rows.all()
#     return roles
#
# @staticmethod
# async def update(role_id: int, changes: dict) -> Role:
#     async with await get_session_db() as session:
#         updated_role = await session.get(Role, role_id)
#         updated_role.update(changes)
#         await session.commit()
#     return updated_role
#
# @staticmethod
# async def delete_by_id(role_id: int) -> None:
#     async with await get_session_db() as session:
#         await session.execute(delete(Role).where(Role.id == role_id))
#         await session.commit()
