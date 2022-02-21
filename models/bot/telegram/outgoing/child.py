from pydantic import BaseModel

from models.bot.item.school import School
from models.bot.item.subclass import Subclass


class Child(BaseModel):
    subclass: Subclass
    school: School
