from models.bot.item.school import School
from models.bot.item.subclass import Subclass
from config import BaseModel
from pydantic import Field


class Child(BaseModel):
    id: int = Field(ge=1, le=2147483647, alias="child_id")
    subclass: Subclass
    school: School
