from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import LessonNumber


class LessonNumbers(BaseModel):
    data: List[LessonNumber]
