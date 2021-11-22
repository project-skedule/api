from pydantic import BaseModel, Field


class School(BaseModel):
    name: str = Field(max_length=200, min_length=10)
