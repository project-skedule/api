from pydantic import BaseModel, Field

from models.bot.telegram.outgoing.parent import Parent
from models.database import RoleEnum


class ParentRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Parent
