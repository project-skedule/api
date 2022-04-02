from config import BaseModel
from pydantic import Field


class Corpus(BaseModel):
    id: int = Field(ge=1, le=2147483647)
    address: str = Field(min_length=10, max_length=250)
    name: str = Field(min_length=1, max_length=100)
