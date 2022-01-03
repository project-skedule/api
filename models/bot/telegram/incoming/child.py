from pydantic import BaseModel, Field


class Child(BaseModel):
    telegram_id: int = Field(ge=1, le=2147483647)
    subclass_id: int = Field(ge=1, le=2147483647)
