from typing import Union

from pydantic import BaseModel, Field

from models.bot.incoming import subclass, teacher


class CertainLesson(BaseModel):
    day_of_week: int = Field(ge=1, le=7)
    lesson_number: int = Field(ge=0, le=20)
    school_id: int = Field(ge=1, le=2147483647)
    data: Union[teacher.Teacher, subclass.Subclass]
