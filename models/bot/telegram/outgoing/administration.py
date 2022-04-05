from models.bot.item.school import School
from config import BaseModel
from pydantic import Field


class Administration(BaseModel):
    id: int = Field(ge=1, le=2147483647, alias="administration_id")
    school: School
