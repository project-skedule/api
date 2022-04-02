from typing import List

from config import BaseModel
from pydantic import Field


class Lesson(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    subject: str = Field(min_length=2, max_length=200)
    lesson_number_id: int = Field(ge=1, le=2147483647)
    teacher_id: int = Field(ge=1, le=2147483647)
    subclasses: List[int]
    cabinet_id: int = Field(ge=1, le=2147483647)
