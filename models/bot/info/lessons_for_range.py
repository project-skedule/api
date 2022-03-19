from typing import List

from models.bot.info.lessons_for_day import LessonsForDay
from pydantic import BaseModel


class LessonsForRange(BaseModel):
    data: List[LessonsForDay]
