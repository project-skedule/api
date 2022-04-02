from typing import List

from models.bot.item import School
from config import BaseModel


class Schools(BaseModel):
    data: List[School]
