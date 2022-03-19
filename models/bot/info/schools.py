from typing import List

from models.bot.item import School
from pydantic import BaseModel


class Schools(BaseModel):
    data: List[School]
