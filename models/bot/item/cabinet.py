from typing import Optional

from pydantic import BaseModel, Field, validator


class Cabinet(BaseModel):
    floor: int = Field(ge=-10, le=100)
    name: str = Field(max_length=100, min_length=1)
