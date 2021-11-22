from pydantic import BaseModel, Field, validator


class Letter(BaseModel):
    letter: str = Field(min_length=1, max_length=50)
