from models.bot.item.school import School
from models.bot.item.subclass import Subclass
from pydantic import BaseModel, Field


class Child(BaseModel):
    child_id: int = Field(ge=1, le=2147483647)
    subclass: Subclass
    school: School
