from pydantic import BaseModel, Field, validator


class LessonNumber(BaseModel):
    id: int = Field(ge=1, le=2147483647)
