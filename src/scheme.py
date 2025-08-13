from typing import Iterable, Any, List

from pydantic import BaseModel

class BaseScheme(BaseModel):

    @classmethod
    def get_schemes_from_models(cls, models: Iterable) -> List[Any]:
        schemes = list()
        for model in models:
            scheme = cls.model_validate(model, from_attributes=True)
            schemes.append(scheme)
        return schemes


class PageScheme(BaseModel):
    offset: int = 0
    limit: int = 10
