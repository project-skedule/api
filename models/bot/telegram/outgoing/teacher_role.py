from models.bot.telegram.outgoing.teacher import Teacher
from models.database import RoleEnum
from config import BaseModel
from pydantic import Field


class TeacherRole(BaseModel):
    id: int
    is_main_role: bool
    role_type: RoleEnum
    teacher: Teacher = Field(alias="data")
