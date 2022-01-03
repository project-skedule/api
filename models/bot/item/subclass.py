from typing import Optional

from pydantic import BaseModel, Field


class Subclass(BaseModel):
    id: Optional[int] = Field(ge=1, le=2147483647)
    educational_level: int = Field(ge=0, le=12)
    identificator: str = Field(max_length=50)
    additional_identificator: str = Field(max_length=50)
