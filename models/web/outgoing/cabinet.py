from pydantic import BaseModel, Field


class Cabinet(BaseModel):
    id: int = Field(ge=1, le=2147483647)
