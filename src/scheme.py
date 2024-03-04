import pydantic


class BaseScheme(pydantic.BaseModel):
    pass


class PageScheme(BaseScheme):
    offset: int = 0
    limit: int = 20
