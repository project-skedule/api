from pydantic import BaseModel, Field

from models.bot.item.school import School
from models.bot.item.subclass import Subclass


class Student(BaseModel):
    subclass: Subclass
    school: School
