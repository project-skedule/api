from config import BaseModel
from pydantic import Field


class Account(BaseModel):
    telegram_id: int = Field(ge=1, le=9223372036854775807)
