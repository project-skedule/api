from models.bot.item.school import School
from pydantic import BaseModel


class Administration(BaseModel):
    school: School
