from typing import Optional

from pydantic import BaseModel, Field


class Corpus(BaseModel):
    address: str = Field(min_length=10, max_length=250)
    name: str = Field(max_length=100)
    canteen_text: Optional[str] = Field(None, min_length=2, max_length=500)
    school_id: int = Field(ge=1, le=2147483647)
