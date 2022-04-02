from typing import List

from models.bot.item import Cabinet
from config import BaseModel


class Cabinets(BaseModel):
    data: List[Cabinet]
