from config import BaseModel
from pydantic import Field


class Group(BaseModel):
    group: str = Field(max_length=50)
