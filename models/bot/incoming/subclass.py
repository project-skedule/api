from pydantic import BaseModel, Field


class Subclass(BaseModel):
    subclass_id: int = Field(ge=1, le=2147483647)
