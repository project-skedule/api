from pydantic import BaseModel, Field


class Canteen(BaseModel):
    corpus_id: int = Field(ge=1, le=2147483647)
