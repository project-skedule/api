from config import BaseModel
from pydantic import Field


class Tag(BaseModel):
    id: int = Field(ge=1, le=2147483647)
    label: str = Field(max_length=50)
