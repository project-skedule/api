from typing import Union

from models.bot.incoming.subclass import Subclass
from models.bot.incoming.teacher import Teacher
from pydantic import BaseModel, Field


class LessonsForRange(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
    start_index: int = Field(ge=1)
    end_index: int = Field(ge=1)
    data: Union[Teacher, Subclass]
