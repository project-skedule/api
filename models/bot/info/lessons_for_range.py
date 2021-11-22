from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.info import LessonsForDay


class LessonsForRange(BaseModel):
    data: List[LessonsForDay]
