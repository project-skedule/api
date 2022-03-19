from typing import List

from models.bot.item.lesson import Lesson
from pydantic import BaseModel


class Lessons(BaseModel):
    data: List[Lesson]
