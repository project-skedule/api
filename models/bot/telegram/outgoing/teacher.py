from models.bot.item.school import School
from config import BaseModel
from pydantic import Field


class Teacher(BaseModel):
    id: int = Field(ge=1, le=2147483647, alias="teacher_id")
    name: str = Field(max_length=200, min_length=1)
    school: School
