from pydantic import BaseModel

from models.bot.telegram.outgoing.teacher import Teacher
from models.database import RoleEnum


class TeacherRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Teacher
