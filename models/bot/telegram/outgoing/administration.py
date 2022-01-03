from pydantic import BaseModel

from models.bot.item.school import School


class Administration(BaseModel):
    school: School
