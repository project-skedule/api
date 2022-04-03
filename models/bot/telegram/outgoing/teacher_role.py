from models.bot.telegram.outgoing.teacher import Teacher
from models.database import RoleEnum
from config import BaseModel


class TeacherRole(BaseModel):
    id: int
    is_main_role: bool
    role_type: RoleEnum
    data: Teacher
