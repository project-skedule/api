from models.bot.telegram.outgoing.administration import Administration
from models.database import RoleEnum
from config import BaseModel


class AdministrationRole(BaseModel):
    id: int
    is_main_role: bool
    role_type: RoleEnum
    data: Administration
