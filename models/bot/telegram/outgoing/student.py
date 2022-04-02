from models.bot.item.school import School
from models.bot.item.subclass import Subclass
from config import BaseModel


class Student(BaseModel):
    subclass: Subclass
    school: School
