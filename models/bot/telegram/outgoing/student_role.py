from models.bot.telegram.outgoing.student import Student
from models.database import RoleEnum
from pydantic import BaseModel


class StudentRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Student
