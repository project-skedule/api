from config import BaseModel
from pydantic import Field


class Letter(BaseModel):
    letter: str = Field(min_length=1, max_length=50)
