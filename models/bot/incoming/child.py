from pydantic import BaseModel, Field


class Child(BaseModel):
    child_id: int = Field(ge=1, le=2147483647)
    telegram_id: int = Field(ge=1, le=9223372036854775807)
