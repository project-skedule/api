from pydantic import BaseModel, Field

from models.bot.item.school import School


class Administration(BaseModel):
    school: School
