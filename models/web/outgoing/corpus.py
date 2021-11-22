from pydantic import BaseModel, Field, validator


class Corpus(BaseModel):
    id: int = Field(ge=1, le=2147483647)
