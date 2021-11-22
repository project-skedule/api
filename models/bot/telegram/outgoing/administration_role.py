from pydantic import BaseModel, Field

from models.bot.telegram.outgoing.administration import Administration
from models.database import RoleEnum


class AdministrationRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Administration
