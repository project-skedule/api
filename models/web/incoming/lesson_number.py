from re import compile, match

from pydantic import BaseModel, Field, validator

time_regex = compile(r"[0-2]?[0-9]:[0-5][0-9]")


class LessonNumber(BaseModel):
    number: int = Field(ge=0, le=20)
    time_start: str = Field(min_length=4, max_length=5)
    time_end: str = Field(min_length=4, max_length=5)
    school_id: int = Field(ge=1, le=2147483647)

    @validator("time_end", "time_start")
    def validate_time(cls, time: str):
        if len(time) == 4:
            time = "0" + time
        elif len(time) != 5:
            raise ValueError("Must be at 5 or 4 characters")
        if not match(time_regex, time):
            raise ValueError("Wrong format")
        return time
