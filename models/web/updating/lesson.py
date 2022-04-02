from typing import List, Optional

from config import BaseModel
from pydantic import Field


class Lesson(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=1, le=7)
    subject: Optional[str] = Field(None, min_length=2, max_length=200)
    lesson_number_id: Optional[int] = Field(None, ge=1, le=2147483647)
    teacher_id: Optional[int] = Field(None, ge=1, le=2147483647)
    cabinet_id: Optional[int] = Field(None, ge=1, le=2147483647)
    subclasses: Optional[List[int]] = Field(None)
    lesson_id: int = Field(ge=1, le=2147483647)
