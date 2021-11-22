from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import Lesson


class LessonsForDay(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    lessons: List[Lesson]
