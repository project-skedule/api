from typing import List
from pydantic import BaseModel, Field


class Teacher(BaseModel):
    id: int = Field(ge=1, le=2147483647)
    name: str = Field(max_length=200, min_length=1)
    tags: List[str] = Field(default_factory=list, max_items=10)
