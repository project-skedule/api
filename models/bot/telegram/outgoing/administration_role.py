from models.bot.telegram.outgoing.administration import Administration
from models.database import RoleEnum
from pydantic import BaseModel


class AdministrationRole(BaseModel):
    is_main_role: bool
    role_type: RoleEnum
    data: Administration
