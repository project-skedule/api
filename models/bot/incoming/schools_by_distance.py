from pydantic import BaseModel, Field, validator


class SchoolsByDistance(BaseModel):
    name: str = Field(max_length=200, min_length=1)
