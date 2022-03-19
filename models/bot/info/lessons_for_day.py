from typing import List

from models.bot.item import Lesson
from pydantic import BaseModel, Field


class LessonsForDay(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    lessons: List[Lesson]
