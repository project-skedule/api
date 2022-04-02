from re import compile as re_compile
from re import match
from typing import Optional

from config import BaseModel
from pydantic import Field, validator

time_regex = re_compile(r"[0-2]?[0-9]:[0-5][0-9]")


class LessonNumber(BaseModel):
    number: Optional[int] = Field(None, ge=0, le=20)
    time_start: Optional[str] = Field(None, min_length=4, max_length=5)
    time_end: Optional[str] = Field(None, min_length=4, max_length=5)
    lesson_number_id: int = Field(ge=1, le=2147483647)

    @validator("time_end", "time_start")
    def validate_time(cls, time: str):
        if len(time) == 4:
            time = "0" + time
        elif len(time) != 5:
            raise ValueError("Must be at 5 or 4 characters")
        if not match(time_regex, time):
            raise ValueError("Wrong format")
        return time
