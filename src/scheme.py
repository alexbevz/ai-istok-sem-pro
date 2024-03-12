from pydantic import BaseModel
from typing import Optional

class BaseScheme(BaseModel):
    pass


class PageScheme(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 20
