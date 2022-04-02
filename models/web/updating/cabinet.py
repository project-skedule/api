from typing import List, Optional

from config import BaseModel
from pydantic import Field


class Cabinet(BaseModel):
    floor: Optional[int] = Field(None, ge=-10, le=100)
    name: Optional[str] = Field(None, max_length=100, min_length=1)
    cabinet_id: int = Field(ge=1, le=2147483647)
    tags: List[str] = Field(default_factory=list, max_items=10)
