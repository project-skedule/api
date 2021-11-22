from pydantic import BaseModel, Field, validator


class Group(BaseModel):
    group: str = Field(max_length=50)
