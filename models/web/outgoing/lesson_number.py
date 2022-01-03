from pydantic import BaseModel, Field


class LessonNumber(BaseModel):
    id: int = Field(ge=1, le=2147483647)
