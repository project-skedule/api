from typing import List
from models.bot.item.corpus import Corpus
from pydantic import BaseModel, Field


class Cabinet(BaseModel):
    id: int = Field(ge=1, le=2147483647)
    floor: int = Field(ge=-10, le=100)
    name: str = Field(max_length=100, min_length=1)
    tags: List[str] = Field(default_factory=list, max_items=10)
    corpus: Corpus
