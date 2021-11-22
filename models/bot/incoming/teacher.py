from pydantic import BaseModel, Field, validator


class Teacher(BaseModel):
    teacher_id: int = Field(ge=1, le=2147483647)
