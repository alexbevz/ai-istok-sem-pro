from typing import Any
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exception import CrudException

class Page:
    offset: Optional[int] = 0
    limit: Optional[int] = 20

    def __init__(self, offset: int = 0, limit: int = 20):
        self.offset: Optional[int] = offset
        self.limit: Optional[int] = limit


class CrudRepository:
    _cls_model: Any

    def __init_subclass__(cls, cls_model: Any = None):
        cls._cls_model = cls_model

    @classmethod
    async def create(cls, *, model: Any, session: AsyncSession) -> Any:
        try:
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return model
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def create_all(cls, *, models: list[Any], session: AsyncSession) -> list[Any]:
        try:
            session.add_all(models)
            await session.flush()
            for item in models:
                await session.refresh(item)
            return models
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def get_by_id(cls, *, model_id: int, session: AsyncSession) -> Any:
        try:
            model = await session.get(cls._cls_model, model_id)
            return model
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def get_by_unique_field(cls, *, field: Any, value: Any, session: AsyncSession) -> Any:
        query = select(cls._cls_model).where(field == value).execution_options(synchronize_session="fetch")
        try:
            model = await session.execute(query)
            return model.scalar()
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def get_all_by_id(cls, *, models_id: list[int], session: AsyncSession) -> list[Any]:
        query = select(cls._cls_model).where(cls._cls_model.id.in_(models_id))
        try:
            models = await session.execute(query)
            return models.scalars().unique().all()
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def get_all_by_field(cls, field: Any, value: Any, session: AsyncSession) -> list[Any]:
        query = select(cls._cls_model).where(field == value).execution_options(synchronize_session="fetch")
        try:
            models = await session.execute(query)
            return models.scalars().unique().all()
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def get_all(cls, *, page: Page, session: AsyncSession) -> list[Any]:
        query = select(cls._cls_model).offset(page.offset).limit(page.limit)
        try:
            models = await session.execute(query)
            return models.scalars().unique().all()
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def update(cls, *, model: Any, session: AsyncSession) -> Any:
        try:
            session.add(model)
            await session.flush()
            return model
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def delete_by_id(cls, *, model_id: int, session: AsyncSession) -> Any:
        try:
            model = await session.get(cls._cls_model, model_id)
            await session.delete(model)
            await session.flush()
            return model
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def delete(cls, *, model: Any, session: AsyncSession) -> Any:
        try:
            await session.delete(model)
            await session.flush()
            return model
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def delete_all_by_id(cls, *, models_id: list[int], session: AsyncSession) -> list[Any]:
        try:
            models = []
            for model_id in models_id:
                result = await session.execute(select(cls._cls_model).where(cls._cls_model.id == model_id))
                model = result.scalar_one()

                await session.delete(model)
                models.append(model)
            await session.flush()
            return models
        except IntegrityError as e:
            raise CrudException(e)

    @classmethod
    async def delete_all_by_field(cls, field: Any, value: Any, session: AsyncSession) -> list[Any]:
        try:
            models = []
            result = await session.execute(select(cls._cls_model).where(field == value))
            model = result.scalars().all()
            for item in model:
                await session.delete(item)
                models.append(item)
            await session.flush()
            return models
        except IntegrityError as e:
            raise CrudException(e)

    #
    # async def search(self, **filters: Any) -> list[Any]:
    #     """search by fields values"""
    #     conditions = [
    #         field == val
    #         for key, val in filters.items()
    #         if (field := inspect(self._cls_model).columns.get(key)) is not None
    #     ]
    #     query = (
    #         select(self._cls_model)
    #         .where(*conditions)
    #         .execution_options(synchronize_session="fetch")
    #     )
    #     rows = await self._session.execute(query)
    #     return rows.scalars().unique().all()
