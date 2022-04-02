from typing import Optional

from config import BaseModel
from pydantic import Field


class School(BaseModel):
    name: Optional[str] = Field(None, max_length=200, min_length=10)
    school_id: int = Field(ge=1, le=2147483647)
