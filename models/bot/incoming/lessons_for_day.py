from typing import Union

from pydantic import BaseModel, Field

from models.bot.incoming.subclass import Subclass
from models.bot.incoming.teacher import Teacher


class LessonsForDay(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    school_id: int = Field(ge=1, le=2147483647)
    data: Union[Teacher, Subclass]
