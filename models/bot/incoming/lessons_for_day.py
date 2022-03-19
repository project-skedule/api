from typing import Union

from models.bot.incoming.subclass import Subclass
from models.bot.incoming.teacher import Teacher
from pydantic import BaseModel, Field


class LessonsForDay(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    school_id: int = Field(ge=1, le=2147483647)
    data: Union[Teacher, Subclass]
