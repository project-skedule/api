from models.bot.telegram.outgoing.administration import Administration
from models.database import RoleEnum
from config import BaseModel
from pydantic import Field


class AdministrationRole(BaseModel):
    id: int
    is_main_role: bool
    role_type: RoleEnum
    administration: Administration = Field(alias="data")
