from typing import Optional

from config import BaseModel
from pydantic import Field


class School(BaseModel):
    id: Optional[int] = Field(ge=1, le=2147483647)
    name: str = Field(max_length=200, min_length=10)
