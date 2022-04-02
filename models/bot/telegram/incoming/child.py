from config import BaseModel
from pydantic import Field


class Child(BaseModel):
    telegram_id: int = Field(ge=1, le=9223372036854775807)
    subclass_id: int = Field(ge=1, le=2147483647)
