from pydantic import BaseModel


class BaseScheme(BaseModel):
    pass


class PageScheme(BaseModel):
    offset: int = 0
    limit: int = 20


class BaseRoleScheme(BaseScheme):
    name: str


class CreatingRoleScheme(BaseRoleScheme):
    pass


class UpdatingRoleScheme(BaseRoleScheme):
    pass


class ModelRoleScheme(BaseRoleScheme):
    id: int


class BaseUserScheme(BaseScheme):
    username: str
    password: str
    email: str


class CreatingUserScheme(BaseUserScheme):
    roles: list[int]


class UpdatingUserScheme(BaseUserScheme):
    roles: list[int]


class ModelUserScheme(BaseUserScheme):
    id: int
    roles: list[ModelRoleScheme]


class BaseAuthScheme(BaseScheme):
    username: str
    password: str


class LoginAuthScheme(BaseAuthScheme):
    pass


class RegisterAuthScheme(BaseAuthScheme):
    email: str = None


class TokensScheme(BaseScheme):
    access_token: str
    refresh_token: str


class RefreshTokenScheme(BaseScheme):
    access_token: str

