from typing import List

from pydantic import BaseModel

from models.bot.item.lesson import Lesson


class Lessons(BaseModel):
    data: List[Lesson]
