from typing import Optional

from pydantic import BaseModel, Field


class Teacher(BaseModel):
    name: Optional[str] = Field(None, max_length=200, min_length=1)
    teacher_id: int = Field(ge=1, le=2147483647)
