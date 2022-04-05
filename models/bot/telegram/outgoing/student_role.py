from models.bot.telegram.outgoing.student import Student
from models.database import RoleEnum
from config import BaseModel
from pydantic import Field


class StudentRole(BaseModel):
    id: int
    is_main_role: bool
    role_type: RoleEnum
    student: Student = Field(alias="data")
