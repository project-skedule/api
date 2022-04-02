from config import BaseModel
from pydantic import Field


class Teacher(BaseModel):
    telegram_id: int = Field(ge=1, le=9223372036854775807)
    teacher_id: int = Field(ge=1, le=2147483647)
