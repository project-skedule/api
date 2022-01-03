from typing import List

from pydantic import BaseModel

from models.bot.item import LessonNumber


class LessonNumbers(BaseModel):
    data: List[LessonNumber]
