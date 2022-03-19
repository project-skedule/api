from typing import List

from models.bot.item import LessonNumber
from pydantic import BaseModel


class LessonNumbers(BaseModel):
    data: List[LessonNumber]
