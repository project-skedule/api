from typing import List

from pydantic import BaseModel

from models.bot.info.lessons_for_day import LessonsForDay


class LessonsForRange(BaseModel):
    data: List[LessonsForDay]
