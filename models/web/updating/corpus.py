from typing import Optional

from config import BaseModel
from pydantic import Field


class Corpus(BaseModel):
    address: Optional[str] = Field(None, min_length=10, max_length=250)
    name: Optional[str] = Field(None, max_length=100)
    canteen_text: Optional[str] = Field(None, max_length=500)
    corpus_id: int = Field(ge=1, le=2147483647)
