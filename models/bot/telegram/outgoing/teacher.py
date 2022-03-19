from models.bot.item.school import School
from pydantic import BaseModel, Field


class Teacher(BaseModel):
    teacher_id: int = Field(ge=1, le=2147483647)
    name: str = Field(max_length=200, min_length=1)
    school: School
