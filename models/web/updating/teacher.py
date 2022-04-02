from typing import List, Optional

from config import BaseModel
from pydantic import Field


class Teacher(BaseModel):
    name: Optional[str] = Field(None, max_length=200, min_length=1)
    teacher_id: int = Field(ge=1, le=2147483647)
    tags: List[str] = Field(default_factory=list, max_items=10)
