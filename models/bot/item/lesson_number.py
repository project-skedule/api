from pydantic import BaseModel, Field


class LessonNumber(BaseModel):
    id: int = Field(ge=0, le=2147483647)
    number: int = Field(ge=0, le=20)
    time_start: str = Field(min_length=5, max_length=5)
    time_end: str = Field(min_length=5, max_length=5)
