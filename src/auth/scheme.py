import pydantic


class BaseModel(pydantic.BaseModel):
    pass


class PageSchema(BaseModel):
    offset: int = 0
    limit: int = 20


class IdSchema(BaseModel):
    id: int


class BaseRoleSchema(BaseModel):
    name: str


class SaveRoleSchema(BaseRoleSchema):
    pass


class UpdateRoleSchema(SaveRoleSchema):
    pass


class ModelRoleSchema(BaseRoleSchema):
    id: int

    class Config:
        fields = {'users': {'exclude': True}}


class BaseUserSchema(BaseModel):
    username: str
    password: str
    email: str


class SaveUserSchema(BaseUserSchema):
    roles: list[int]


class UpdateUserSchema(SaveUserSchema):
    pass


class ModelUserSchema(BaseUserSchema):
    id: int
    roles: list[ModelRoleSchema]
