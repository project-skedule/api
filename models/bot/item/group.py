from pydantic import BaseModel, Field


class Group(BaseModel):
    group: str = Field(max_length=50)
