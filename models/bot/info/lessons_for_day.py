from typing import List

from models.bot.item import Lesson
from config import BaseModel
from pydantic import Field


class LessonsForDay(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    lessons: List[Lesson]
