from typing import List

from models.bot.item import LessonNumber
from config import BaseModel


class LessonNumbers(BaseModel):
    data: List[LessonNumber]
