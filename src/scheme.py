from pydantic import BaseModel


class BaseScheme(BaseModel):
    pass


class PageScheme(BaseModel):
    offset: int = 0
    limit: int = 20
