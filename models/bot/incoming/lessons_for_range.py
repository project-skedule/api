from typing import Union

from pydantic import BaseModel, Field

from models.bot.incoming.subclass import Subclass
from models.bot.incoming.teacher import Teacher


class LessonsForRange(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
    start_index: int = Field(ge=1)
    end_index: int = Field(ge=1)
    data: Union[Teacher, Subclass]
