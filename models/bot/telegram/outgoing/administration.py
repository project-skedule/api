from models.bot.item.school import School
from config import BaseModel


class Administration(BaseModel):
    school: School
