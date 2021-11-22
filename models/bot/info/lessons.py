from typing import List

from pydantic import BaseModel, Field, validator

from models.bot import item


class Lessons(BaseModel):
    data: List[item.Lesson]
