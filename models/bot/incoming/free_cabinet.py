from typing import Optional

from config import BaseModel
from pydantic import Field


class FreeCabinet(BaseModel):
    corpus_id: int = Field(ge=1, le=2147483647)
    day_of_week: int = Field(ge=1, le=7)
    lesson_number: Optional[int] = Field(ge=0, le=20)
    floor: Optional[int] = Field(None, ge=-10, le=100)
