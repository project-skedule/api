from models.bot.telegram.outgoing.parent import Parent
from models.database import RoleEnum
from config import BaseModel


class ParentRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Parent
