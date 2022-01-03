from typing import List

from pydantic import BaseModel

from models.bot.item import School


class Schools(BaseModel):
    data: List[School]
