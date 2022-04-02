from typing import List, Optional
from config import BaseModel
from pydantic import Field


class Cabinet(BaseModel):
    floor: int = Field(ge=-10, le=100)
    name: str = Field(max_length=100, min_length=1)
    corpus_id: int = Field(ge=1, le=2147483647)
    tags: List[str] = Field(default_factory=list, max_items=10)
