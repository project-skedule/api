from typing import Union

from models.bot.incoming.subclass import Subclass
from models.bot.incoming.teacher import Teacher
from config import BaseModel
from pydantic import Field


class CertainLesson(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    lesson_number: int = Field(ge=0, le=20)
    school_id: int = Field(ge=1, le=2147483647)
    data: Union[Teacher, Subclass]
