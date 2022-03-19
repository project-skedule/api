from models.bot.telegram.outgoing.teacher import Teacher
from models.database import RoleEnum
from pydantic import BaseModel


class TeacherRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Teacher
