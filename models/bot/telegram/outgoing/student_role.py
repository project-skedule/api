from pydantic import BaseModel

from models.bot.telegram.outgoing.student import Student
from models.database import RoleEnum


class StudentRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Student
