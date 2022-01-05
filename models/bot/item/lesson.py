from typing import List

from pydantic import BaseModel, Field

from models.bot.item.cabinet import Cabinet
from models.bot.item.subclass import Subclass
from models.bot.item.teacher import Teacher
from models.bot.item.lesson_number import LessonNumber


class Lesson(BaseModel):
    lesson_number: LessonNumber
    day_of_week: int = Field(ge=1, le=7)
    subject: str = Field(max_length=200)
    subclasses: List[Subclass]
    teacher: Teacher
    cabinet: Cabinet
